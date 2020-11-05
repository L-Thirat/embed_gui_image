# todo right click to prev draw/original
# todo canvas draw only in image.org
# todo config camera bar gui/cv2

# **Importance**
# todo ** tinkboard install
# todo ** need area/pos ?

import tkinter as tki
from tkinter import filedialog
import cv2
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import imutils
import datetime
import numpy as np
import json
import glob
import os
import time

# Testing
DEBUG = True
TEST_MAMOS = False

# Config
full_w = 1350
camera_h = 480
camera_w = 640
out_path = "output/original/"
cp_path = "output/compare/"


# TODO MAMOS
if TEST_MAMOS:
    import ASUS.GPIO as GPIO

    LED = 164
    BTN_input = 167

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.ASUS)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(BTN_input, GPIO.IN)


def control(pin, signal):
    if signal:
        GPIO.output(pin, GPIO.HIGH)
        print("ON")
    else:
        GPIO.output(pin, GPIO.LOW)
        print("OFF")
    time.sleep(1)


class App:
    def __init__(self, window, window_title):
        self.file_path_o = ""
        self.file_path_c = ""
        self.photo_rt = None
        self.photo_org = None
        self.photo_cp = None
        self.load_img_o = None
        self.load_img_cp = None
        self.load_draw = None

        # Create Control Bar
        cv2.namedWindow("Parameters")
        cv2.resizeWindow("Parameters", 640, 240)
        cv2.createTrackbar("Threshold1", "Parameters", 42, 255, self.empty)
        cv2.createTrackbar("Threshold2", "Parameters", 0, 255, self.empty)
        cv2.createTrackbar("Area", "Parameters", 100, 60000, self.empty)
        self.window = window
        self.window.geometry("1800x900")
        self.window.title(window_title)
        self.window.resizable(1, 1)
        self.window.configure(background="#d9d9d9")

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture()

        # Button that lets the user take a snapshot
        self.btn_snapshot = tki.Button(window, text="Snapshot", width=40, height=3, command=self.snapshot_origin)
        self.btn_snapshot.place(relx=0.41, rely=0.05)

        self.btn_save = tki.Button(window, text="Save", width=40, height=3, command=self.save_draw)
        self.btn_save.place(relx=0.61, rely=0.05)

        self.load_filename = None
        self.browsebutton = tki.Button(window, text="Browse", width=40, height=3, command=self.browsefunc)
        self.browsebutton.place(relx=0.81, rely=0.05)

        if not TEST_MAMOS:
            self.btn_compare = tki.Button(window, text="Compare", width=40, height=3, command=self.snapshot_compare)
            self.btn_compare.place(relx=0.41, rely=0.15)

        self.btn_reset = tki.Button(window, text="Reset", width=40, height=3, command=self.reset)
        self.btn_reset.place(relx=0.61, rely=0.15)

        self.pathlabel = tki.Label(window)
        self.pathlabel.place(relx=0.41, rely=0.25)

        # Create a canvas that can fit the above video source size
        self.canvas_rt = tki.Canvas(window)
        self.canvas_rt.place(relx=0.01, rely=0.05)
        self.canvas_rt.config(width=camera_w / 2, height=camera_h / 2)

        self.canvas2 = tki.Canvas(window, cursor="cross")
        self.canvas2.place(relx=0.1, rely=0.4)
        # >> additional
        self.x = self.y = 0
        self.count_draw = 0
        self.raw_data_draw = {"filename": ""}
        self.canvas2.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas2.bind("<B1-Motion>", self.on_move_press)
        self.canvas2.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas2.bind("<Button-3>", self.undo)
        self.rect = []
        self.start_x = None
        self.start_y = None
        # <<
        self.canvas2.config(width=camera_w, height=camera_h)

        self.canvas3 = tki.Canvas(window)
        self.canvas3.place(relx=0.5, rely=0.4)
        self.canvas3.config(width=camera_w, height=camera_h)

        # Check latest data
        list_of_files = glob.glob('data/*')  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        if latest_file:
            self.read_raw_data(latest_file)

        # # After it is called once, the update method will be automatically called every delay milliseconds

        self.delay = 15
        self.update()

        self.window.mainloop()

    def empty(self, a):
        pass

    def update(self):
        # TODO MAMOS
        try:
            if GPIO.input(BTN_input):
                control(pin=LED, signal=False)  # is pressed
                print("ON")
                self.snapshot("compare")
            else:
                control(pin=LED, signal=True)  # is not pressed
        except KeyboardInterrupt:
            GPIO.cleanup()        # Get a frame from the video source

        ret, frame = self.vid.get_frame()

        if ret:
            frame = imutils.resize(frame, height=int(camera_h / 2), width=int(camera_w / 2))
            cv_frame = Image.fromarray(frame)
            self.photo_rt = ImageTk.PhotoImage(image=cv_frame)
            self.canvas_rt.create_image(0, 0, image=self.photo_rt, anchor=tki.NW)

        self.window.after(self.delay, self.update)

    def reset(self):
        self.canvas2.delete("all")
        self.canvas3.delete("all")
        self.raw_data_draw = {"filename": ""}
        self.pathlabel.config(text="")

    def on_button_press(self, event):
        self.flag_press = False
        # save mouse drag start position
        self.start_x = self.canvas2.canvasx(event.x)
        self.start_y = self.canvas2.canvasy(event.y)

        # create rectangle if not yet exist
        self.rect.append(self.canvas2.create_rectangle(self.x, self.y, 1, 1, outline='red'))

    def on_move_press(self, event):
        self.flag_press = True
        cur_x = self.canvas2.canvasx(event.x)
        cur_y = self.canvas2.canvasy(event.y)
        self.canvas2.coords(self.rect[-1], self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        if self.flag_press:
            self.count_draw += 1
            cur_x = self.canvas2.canvasx(event.x)
            cur_y = self.canvas2.canvasy(event.y)
            self.raw_data_draw[self.count_draw] = {"rect": [self.start_x, self.start_y, cur_x, cur_y]}

    def undo(self, event):
        if self.count_draw:
            del self.raw_data_draw[self.count_draw]
            self.canvas2.delete(self.count_draw+1)
            self.count_draw -= 1

    def snapshot(self, mode):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        if ret:
            if mode == "original":
                self.file_path_o = out_path + "o_" + filename
                cv2.imwrite(self.file_path_o, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                if DEBUG:
                    self.load_img_o = Image.open(out_path + "o_2020-11-05_14-38-30.jpg")
                else:
                    self.load_img_o = Image.open(self.file_path_o)
                size = [camera_w, camera_h, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.photo_org, anchor=tki.NW)
            elif mode == "compare":
                self.file_path_c = cp_path + "c_" + filename
                # if DEBUG:
                #     self.load_img_cp = Image.open(cp_path + "c_2020-11-05_14-53-29.jpg")
                # else:
                cv2.imwrite(self.file_path_c, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_cp = Image.open(self.file_path_c)

                size = [camera_w, camera_h, 0, 0]
                self.load_img_cp = self.load_img_cp.resize((size[0], size[1]), Image.ANTIALIAS)
                cp_result = self.detect_compare()
                self.photo_cp = ImageTk.PhotoImage(image=self.load_img_cp)
                self.canvas3.create_image(size[2], size[3], image=self.photo_cp, anchor=tki.NW)
                self.load_rect(self.canvas3, self.load_draw, cp_result)
                self.load_draw = {}

    @staticmethod
    def load_rect(cvs, data, result=None):
        for key, val in data.items():
            if key != "filename":
                if result:
                    color = result[key]
                else:
                    color = "red"
                cvs.create_rectangle(val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3], outline=color)
                cvs.create_text((val["rect"][2], val["rect"][3]), text=key, font=('Impact', -15), fill="yellow")

    def snapshot_origin(self):
        self.snapshot("original")

    def snapshot_compare(self):
        self.snapshot("compare")

    def save_draw(self):
        self.count_draw = 0
        copy_image = self.load_img_o.copy()
        for key, val in self.raw_data_draw.items():
            if key != "filename":
                x1, y1, x2, y2 = val["rect"]
                if x1 > x2:
                    x1, x2 = x2, x1
                if y1 > y2:
                    y1, y2 = y2, y1
                image_area = copy_image.crop((x1, y1, x2, y2))
                if (image_area.size[0] != 0) and (image_area.size[1] != 0):
                    self.raw_data_draw[key]["rect"] = [x1, y1, x2, y2]
            else:
                self.raw_data_draw["filename"] = self.file_path_o

        # todo need test
        data = json.dumps(self.raw_data_draw)
        with open('data/data_%s.json' % self.file_path_o[:-4].replace("output/", ""), 'w') as fp:
            fp.write(data)
        print("SAVE !", 'data/data_%s.json' % self.file_path_o[:-4].replace("output/", ""))
        self.raw_data_draw = {"filename": ""}

    def detect_compare(self):
        result = {}
        if self.load_filename:
            with open(self.load_filename, 'r') as fp:
                self.load_draw = json.load(fp)
        else:
            try:
                with open('data/data_%s.json' % self.file_path_o[:-4].replace("output/original/", ""), 'r') as fp:
                    self.load_draw = json.load(fp)
            except Exception as e:
                print(self.file_path_o)

                raise e
        for key, val in self.load_draw.items():
            if key != "filename":
                image_area = self.load_img_cp.crop((val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3]))
                print(image_area.size)
                open_cv_image = np.array(image_area, dtype=np.uint8)
                img_dil = self.image_preprocessors(open_cv_image)
                cv2.imwrite("test_cp.jpg", img_dil)
                # data_result = self.get_contours(img_dil)

                image_o_area = self.load_img_o.crop(
                    (val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3]))  # // = image_o fill
                image_o_area = np.array(image_o_area, dtype=np.uint8)
                image_cp_area = np.array(image_area, dtype=np.uint8)
                # cv2.imshow("result1", image_o_area) # show prepossess image result
                # cv2.imshow("result2", image_cp_area) # show prepossess image result
                score = self.cp_similarity(image_o_area, image_cp_area)
                print(score)
                # if data_result:
                #     x, y, area, points = data_result
                # thershold_percent = 10
                thershold_score = 20
                if score >= thershold_score:
                    # and ((abs(area - self.load_draw[key]["area"]) * 100) / self.load_draw[key]["area"] <
                    # thershold_percent): print("True", key, area, self.load_draw[key]["area"])
                    print("item %s => " % key + "True")
                    result[key] = "green"
                else:
                    print("item %s => " % key + "False")
                    result[key] = "red"
                # else:
                #     print("item %s => " % key + "False")
                #     result[key] = "red"

        return result

    def read_raw_data(self, filename):
        if filename:
            with open(filename, 'r') as fp:
                self.load_draw = json.load(fp)

                # load img
                print(self.load_draw)
                self.load_img_o = Image.open(self.load_draw["filename"])
                self.file_path_o = self.load_draw["filename"]
                size = [camera_w, camera_h, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.photo_org, anchor=tki.NW)

                # load draw
                self.load_rect(self.canvas2, self.load_draw)

    def browsefunc(self):
        self.load_filename = filedialog.askopenfilename()
        self.pathlabel.config(text=self.load_filename)
        self.read_raw_data(self.load_filename)

    # >> image processing
    @staticmethod
    def cp_similarity(original, image_to_compare):
        sift = cv2.xfeatures2d.SIFT_create()
        kp_1, desc_1 = sift.detectAndCompute(original, None)
        kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)

        index_params = dict(algorithm=0, trees=5)
        search_params = dict()
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(desc_1, desc_2, k=2)

        good_points = []
        ratio = 0.6
        for m, n in matches:
            if m.distance < ratio * n.distance:
                good_points.append(m)
        return (len(good_points) * 100) / len(matches)

    @staticmethod
    def get_contours(img):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # >>> Find original position
        # item_area = 10000  # minimum area of item
        original_x, original_y = 0, 0
        original_area = 0
        if len(contours) == 1:
            # todo fix not check from len
            approx = []
            for cnt in contours:
                area = cv2.contourArea(cnt)

                # if area > item_area:
                M = cv2.moments(cnt)

                original_area = area
                original_x = int(M['m10'] / M['m00'])
                original_y = int(M['m01'] / M['m00'])

                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            return original_x, original_y, original_area, len(approx)

    @staticmethod
    def image_preprocessors(img):
        # imgContour = img.copy()
        img_blur = cv2.GaussianBlur(img, (7, 7), 1)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
        threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
        img_canny = cv2.Canny(img_gray, threshold1, threshold2)  # 255 # todo create tuning bar gui
        kernel = np.ones((5, 5))
        img_dil = cv2.dilate(img_canny, kernel, iterations=1)

        return img_dil

    # << image processing


class MyVideoCapture:
    def __init__(self):
        # Open the video source
        if DEBUG:
            self.vid = cv2.VideoCapture("sample1.mp4")
        else:
            for i in range(10):
                self.vid = cv2.VideoCapture(i)
                if self.vid.isOpened():
                    break

            # Get video source width and height
            self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
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


App(tki.Tk(), "Tkinter and OpenCV")