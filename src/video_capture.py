import cv2
from src import preprocess as pp
from src import extraction as et
import imutils
import numpy as np
import glob


class MyVideoCapture:
    def __init__(self, DEBUG):
        """ Video config"""
        self.DEBUG = DEBUG
        self.start_rgb = (0, 0, 0)
        #  open video source (by default this will try to open the computer webcam)
        if "sample_img" in DEBUG:
            sample_source = DEBUG["sample_img"]
            self.sample_sources = []
            self.cam_width = DEBUG["cam_width"]
            self.cam_height = DEBUG["cam_height"]
            if sample_source[-4:] == ".png" or self.DEBUG["sample_img"][-4:] == ".jpg":
                self.vid = cv2.imread(sample_source)
            else:
                self.sample_sources = glob.glob('%s*' % sample_source)
                self.cur_debug = 0
                self.vid = cv2.imread(self.sample_sources[self.cur_debug])
        else:
            for i in range(10):
                self.vid = cv2.VideoCapture(i)
                if self.vid.isOpened():
                    break

            # Get video source width and height
            self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_original_frame(self, config):
        if "sample_img" in self.DEBUG:
            if self.sample_sources:
                self.vid = cv2.imread(self.sample_sources[self.cur_debug])
            origin_image = self.vid
            origin_image = cv2.resize(origin_image, (self.cam_width, self.cam_height),
                                      interpolation=cv2.INTER_AREA)
        else:
            if self.vid.isOpened():
                ret, origin_image = self.vid.read()
                if not ret:
                    return ret, None, None, None
            else:
                raise Exception("Camera not opening")

        t_zoom = config["t_zoom"]
        if t_zoom > 1:
            origin_image = self.zoom(origin_image, t_zoom)

        return origin_image

    def get_frame(self, config, raw_data_draw=None, auto_calibrate=False, reset=True):
        """ Get frame from video source"""
        if raw_data_draw is None:
            raw_data_draw = {}
        t_red_min, t_red_max = config["t_red"]["min"], config["t_red"]["max"]
        t_green_min, t_green_max = config["t_green"]["min"], config["t_green"]["max"]
        t_blue_min, t_blue_max = config["t_blue"]["min"], config["t_blue"]["max"]
        t_contrast = config["t_contrast"]
        t_light = config["t_light"]
        t_blur = (2 * (config["t_blur"] - 1)) + 1
        t_noise = config["t_noise"]

        selected_area = self.get_original_frame(config)

        if raw_data_draw["area"]:
            selected_area = pp.crop_img(selected_area, raw_data_draw["area"][0])

        # Remove noise
        # ## (2) Morph-op to remove noise
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        # morphed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        selected_area = cv2.medianBlur(selected_area, t_blur)

        # Remove Shadow
        # img = pp.shadow_remove(img)
        # selected_area = pp.color_shadow_remove(selected_area)

        lower_hue = np.array([t_red_min, t_green_min, t_blue_min])
        upper_hue = np.array([t_red_max, t_green_max, t_blue_max])
        # todo run on RUN mode
        # todo rgb control -> gui slow**
        if not auto_calibrate:
            img = pp.brightness(selected_area, t_light, t_contrast)

            # # define range of a color in HSV
            # lower_hue = np.array([t_red_min, t_green_min, t_blue_min])
            # upper_hue = np.array([t_red_max, t_green_max, t_blue_max])
        else:
            # # image pre-process
            b, g, r = cv2.split(selected_area)
            cur_red = int(sum(r.ravel() / len(r.ravel())))
            cur_green = int(sum(g.ravel() / len(g.ravel())))
            cur_blue = int(sum(b.ravel() / len(b.ravel())))
            if self.start_rgb == (0, 0, 0):
                diff_rgb = 0
                self.start_rgb = (cur_red, cur_green, cur_blue)
            else:
                diff_rgb = int(((self.start_rgb[0] - cur_red) + (self.start_rgb[1] - cur_green) + (
                            self.start_rgb[2] - cur_blue)) / 3)

            img = pp.brightness(selected_area, -230 - diff_rgb, -15)

            img, alpha, beta = pp.automatic_brightness_and_contrast(img)
            # b, g, r = cv2.split(img)
            # cur_red = int(sum(r.ravel() / len(r.ravel())))
            # cur_green = int(sum(g.ravel() / len(g.ravel())))
            # cur_blue = int(sum(b.ravel() / len(b.ravel())))
            # if self.start_rgb == (0, 0, 0) or reset:
            #     diff_rgb = (0, 0, 0)
            #     self.start_rgb = (cur_red, cur_green, cur_blue)
            # else:
            #     diff_rgb = (self.start_rgb[0] - cur_red, self.start_rgb[1] - cur_green, self.start_rgb[2] - cur_blue)
            # print("diff_rgb: ", diff_rgb, self.start_rgb, (cur_red, cur_green, cur_blue))
            # lower_hue = np.array(
            #     [(t_red_min - (diff_rgb[0] * 1)), (t_green_min - (diff_rgb[1] * 1)), (t_blue_min - (diff_rgb[2] * 1))])
            # upper_hue = np.array(
            #     [(t_red_max - (diff_rgb[0] * 1)), (t_green_max - (diff_rgb[1] * 1)), (t_blue_max - (diff_rgb[2] * 1))])

            # todo lightness control
            # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # diff_rgb = 255 - int(hsv[-1][-1][-1])
            # print(diff_rgb)
            # lower_hue = np.array([t_red_min, t_green_min, t_blue_min])
            # upper_hue = np.array([t_red_max-diff_rgb, t_green_max-diff_rgb, t_blue_max-diff_rgb])

        # define range of a color in HSV
        lower_hue = np.array([t_red_min, t_green_min, t_blue_min])
        upper_hue = np.array([t_red_max, t_green_max, t_blue_max])
        mask = pp.hue(img, lower_hue, upper_hue)

        # contour extraction
        draw_cnt, contours = et.draw_contour(img, mask)
        select_contour, mask = et.contour_selection(contours, img, t_noise)

        return True, selected_area, select_contour, mask

    @staticmethod
    def zoom(cv2Object, zoomSize):
        """ Resizes the image/video frame to the specified amount of "zoomSize"""
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

    def __del__(self):
        """ Release the video source when the object is destroyed"""
        if self.vid.isOpened():
            self.vid.release()
