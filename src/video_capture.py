import cv2
from src import preprocess as pp
from src import extraction as et
import imutils
import numpy as np

class MyVideoCapture:
    def __init__(self, DEBUG):
        self.DEBUG = DEBUG
        self.start_rgb = (0, 0, 0)
        # Open the video source
        if "sample_img" in DEBUG:
            sample_source = DEBUG["sample_img"]
            self.cam_width = DEBUG["cam_width"]
            self.cam_height = DEBUG["cam_height"]
            self.vid = cv2.imread(sample_source)
        else:
            for i in range(10):
                self.vid = cv2.VideoCapture(i)
                if self.vid.isOpened():
                    break

            # Get video source width and height
            self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self, config, raw_data_draw=None):
        if raw_data_draw is None:
            raw_data_draw = {}
        t_red_min, t_red_max = config["t_red"]["min"], config["t_red"]["max"]
        t_green_min, t_green_max = config["t_green"]["min"], config["t_green"]["max"]
        t_blue_min, t_blue_max = config["t_blue"]["min"], config["t_blue"]["max"]
        t_contrast = config["t_contrast"]
        t_light = config["t_light"]
        t_zoom = config["t_zoom"]
        t_blur = (2*(config["t_blur"]-1)) + 1

        # define range of a color in HSV
        lower_hue = np.array([t_red_min, t_green_min, t_blue_min])
        upper_hue = np.array([t_red_max, t_green_max, t_blue_max])

        if "sample_img" in self.DEBUG:
            selected_area = self.vid
            selected_area = cv2.resize(selected_area, (self.cam_width, self.cam_height),
                                       interpolation=cv2.INTER_AREA)
        else:
            if self.vid.isOpened():
                ret, selected_area = self.vid.read()
                if not ret:
                    return ret, None, None, None
            else:
                raise Exception("Camera not opening")
        if t_zoom > 1:
            selected_area = self.zoom(selected_area, t_zoom)

        if raw_data_draw["area"]:
            selected_area = pp.crop_img(selected_area, raw_data_draw["area"])

        # Remove noise
        # ## (2) Morph-op to remove noise
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        # morphed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        selected_area = cv2.medianBlur(selected_area, t_blur)

        # image pre-process
        img = pp.brightness(selected_area, t_light, t_contrast)

        # todo no control
        mask = pp.hue(img, lower_hue, upper_hue)

        # todo run on RUN mode
        # todo rgb control -> gui slow**
        # b, g, r = cv2.split(img)
        # cur_red = int(sum(r.ravel()/len(r.ravel())))
        # cur_green = int(sum(g.ravel()/len(g.ravel())))
        # cur_blue = int(sum(b.ravel()/len(b.ravel())))
        # if self.start_rgb == (0, 0, 0):
        #     diff_rgb = (0, 0, 0)
        #     self.start_rgb = (cur_red, cur_green, cur_blue)
        # else:
        #     diff_rgb = (self.start_rgb[0] - cur_red, self.start_rgb[1] - cur_green, self.start_rgb[2] - cur_blue)
        # mask = pp.hue(img, (t_red - diff_rgb[0])*3, (t_green - diff_rgb[1])*3, (t_blue - diff_rgb[2])*3)

        # todo lightness control
        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # diff_rgb = 255 - int(hsv[-1][-1][-1])
        # print(diff_rgb)
        # mask = pp.hue(img, t_red-diff_rgb, t_green-diff_rgb, t_blue-diff_rgb)

        # contour extraction
        draw_cnt, contours = et.draw_contour(img, mask)
        select_contour, mask = et.contour_selection(contours, img)

        return True, selected_area, select_contour, mask

    @staticmethod
    def zoom(cv2Object, zoomSize):
        # Resizes the image/video frame to the specified amount of "zoomSize".
        # A zoomSize of "2", for example, will double the canvas size
        cv2Object = imutils.resize(cv2Object, width=(zoomSize * cv2Object.shape[1]))
        # center is simply half of the height & width (y/2,x/2)
        center = (int(cv2Object.shape[0] / 2), int(cv2Object.shape[1] / 2))
        # cropScale represents the top left corner of the cropped frame (y/x)
        cropScale = (int(center[0] / zoomSize), int(center[1] / zoomSize))
        # The image/video frame is cropped to the center with a size of the original picture
        # image[y1:y2,x1:x2] is used to iterate and grab a portion of an image
        # (y1,x1) is the top left corner and (y2,x1) is the bottom right corner of new cropped frame.
        cv2Object = cv2Object[cropScale[0]:center[0] + cropScale[0], cropScale[1]:center[1] + cropScale[1]]
        return cv2Object

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
