import cv2
from src import preprocess as pp
from src import extraction as et


class MyVideoCapture:
    def __init__(self, DEBUG):
        self.DEBUG = DEBUG
        sample_source = DEBUG["sample_img"]
        self.cam_width = DEBUG["cam_width"]
        self.cam_height = DEBUG["cam_height"]

        # Open the video source
        if DEBUG:
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

        if self.DEBUG:
            selected_area = self.vid
            selected_area = cv2.resize(selected_area, (self.cam_width, self.cam_height), interpolation=cv2.INTER_AREA)

            if "area" in raw_data_draw:
                selected_area = pp.crop_img(selected_area, raw_data_draw["area"])

            # image pre-process
            img = pp.brightness(selected_area, t_light, t_contrast)
            mask = pp.hue(img, t_red, t_green, t_blue)

            # contour extraction
            draw_cnt, contours = et.draw_contour(img, mask)
            select_contour, mask = et.contour_selection(contours, img)

            return True, selected_area, select_contour, mask
        else:
            if self.vid.isOpened():
                ret, frame = self.vid.read()
                if ret:
                    # Return a boolean success flag and the current frame converted to BGR
                    return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    return ret, None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
