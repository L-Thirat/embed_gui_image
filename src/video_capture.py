import cv2
from src import preprocess as pp
from src import extraction as et
import imutils


class MyVideoCapture:
    def __init__(self, DEBUG):
        self.DEBUG = DEBUG
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

        t_red = config["t_red"]
        t_green = config["t_green"]
        t_blue = config["t_blue"]
        t_contrast = config["t_contrast"]
        t_light = config["t_light"]
        t_zoom = config["t_zoom"]

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

        if "area" in raw_data_draw:
            selected_area = pp.crop_img(selected_area, raw_data_draw["area"])

        # selected_area = cv2.bilateralFilter(selected_area, 21,51,51)
        selected_area = cv2.medianBlur(selected_area, 7)

        # image pre-process
        img = pp.brightness(selected_area, t_light, t_contrast)

        mask = pp.hue(img, t_red, t_green, t_blue )

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
