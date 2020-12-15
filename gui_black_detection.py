# todo config camera bar gui/cv2 in tkinter
# todo clear image in "/output/o_.jpg"

"""
check linear line
http://www.webmath.com/_answer.php
Iterporation
https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
"""

import tkinter as tki
from tkinter import filedialog
from tkinter import messagebox
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
import atexit
import yaml
from itertools import tee
from scipy.stats import linregress
from statistics import mean
import math
from scipy import interpolate
import matplotlib.pyplot as plt

from src import preprocess as pp
from src import extraction as et
from src import linear_processing as lp
from src.video_capture import MyVideoCapture as vc

global t_dist
global t_num_error

# Setting
with open(r'setting.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    setting_data = yaml.load(file, Loader=yaml.FullLoader)

    cam_height = setting_data["cam_height"]
    cam_width = setting_data["cam_width"]
    out_path = setting_data["out_path"]
    cp_path = setting_data["cp_path"]
    LED_OK = setting_data["LED_OK"]
    LED_NG = setting_data["LED_NG"]
    BTN_input = setting_data["BTN_INPUT"]

    # Testing
    DEBUG = {"sample_img": 'WIN_20201210_10_12_37_Pro.jpg', "cam_width": cam_width,
             "cam_height": cam_height}  # Debug mode -> test from video source
    TEST_MAMOS = False  # TEST MAMOS mode -> use Mamos's button instead GUI

    if TEST_MAMOS:
        from src.mamos import Mamos

        mm = Mamos(LED_OK, LED_NG, BTN_input)

original_threshold_dist = 4
mini_sampling = 4


def empty(area):
    pass


def fix_width(error_width=0):
    width = original_threshold_dist
    if width > error_width:
        width -= error_width
    return width


# Create Control Bar
cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 800, 400)
cv2.createTrackbar("threshold_red", "Parameters", 255, 255, empty)
cv2.createTrackbar("threshold_green", "Parameters", 255, 255, empty)
cv2.createTrackbar("threshold_blue", "Parameters", 105, 255, empty)
cv2.createTrackbar("threshold_light", "Parameters", 0, 255, empty)
cv2.createTrackbar("threshold_contrast", "Parameters", 0, 255, empty)
cv2.createTrackbar("threshold_dist", "Parameters", 10, 100, empty)
cv2.createTrackbar("threshold_num_error", "Parameters", 10, 100, empty)


class App:
    def __init__(self, window, window_title):
        self.config = None

        # Load data
        self.file_path_o = ""
        self.file_path_c = ""
        self.tk_photo_line = None
        self.tk_photo_org = None
        self.tk_photo_cp = None
        self.load_img_o = None
        self.load_img_cp = None
        self.raw_data_draw = {"filename": ""}

        # Visualize output
        self.contour = []
        self.detect_line = {}
        self.error_box = {}
        self.error_line = {}

        # Tkinter setting
        self.window = window
        self.window.geometry("1800x900")
        self.window.title(window_title)
        self.window.resizable(1, 1)
        self.window.configure(background="#d9d9d9")

        # open video source (by default this will try to open the computer webcam)
        self.vid = vc(DEBUG)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tki.Button(window, text="Snapshot", width=40, height=3, command=self.snapshot_origin)
        self.btn_snapshot.place(relx=0.41, rely=0.05)

        self.btn_save = tki.Button(window, text="Save", width=40, height=3, command=self.save_draw)
        self.btn_save.place(relx=0.61, rely=0.05)

        self.load_filename = None
        self.browsebutton = tki.Button(window, text="Browse", width=40, height=3, command=self.browsefunc)
        self.browsebutton.place(relx=0.81, rely=0.05)

        self.btn_compare = tki.Button(window, text="Compare", width=40, height=3, command=self.snapshot_compare)
        self.btn_compare.place(relx=0.41, rely=0.15)

        self.btn_reset = tki.Button(window, text="Reset", width=40, height=3, command=self.reset)
        self.btn_reset.place(relx=0.61, rely=0.15)

        # todo 3 modes for draw
        self.btn_drawmode_detect = tki.Button(window, text="Detect", width=10, height=3, command=self.drawmode_detect,
                                              bg='green')
        self.btn_drawmode_detect.place(relx=0.81, rely=0.15)
        self.btn_drawmode_area = tki.Button(window, text="Area", width=10, height=3, command=self.drawmode_area)
        self.btn_drawmode_area.place(relx=0.86, rely=0.15)
        self.btn_drawmode_ignore = tki.Button(window, text="Ignore", width=10, height=3, command=self.drawmode_ignore)
        self.btn_drawmode_ignore.place(relx=0.91, rely=0.15)

        self.pathlabel = tki.Label(window)
        self.pathlabel.place(relx=0.41, rely=0.25)

        # Create a canvas that can fit the above video source size
        self.canvas_rt = tki.Canvas(window)
        self.canvas_rt.place(relx=0.01, rely=0.05)
        self.canvas_rt.config(width=cam_width / 2, height=cam_height / 2)

        self.canvas2 = tki.Canvas(window, cursor="cross")
        self.canvas2.place(relx=0.1, rely=0.4)

        # Drawing cv2
        self.canvas2.bind("<ButtonPress-1>", self.on_button_press)
        # self.canvas2.bind("<B1-Motion>", self.on_move_press)
        # self.canvas2.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas2.bind("<Button-3>", self.undo)
        self.canvas2.config(width=cam_width, height=cam_height)
        self.start_x = None
        self.start_y = None
        self.prev_line = []
        self.prev_sub_pol = []
        self.prev_pol = []
        self.count_draw_line = 0
        self.count_draw_sub_pol = 0
        self.drawmode = "detect"
        self.polygon_data = []

        # Check latest data
        list_of_files = glob.glob('data/*')  # * means all if need specific format then *.csv
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            self.read_raw_data(latest_file)

        self.canvas3 = tki.Canvas(window)
        self.canvas3.place(relx=0.5, rely=0.4)
        self.canvas3.config(width=cam_width, height=cam_height)

        # # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        global original_threshold_dist
        global t_dist
        global t_num_error
        t_red = cv2.getTrackbarPos("threshold_red", "Parameters")
        t_green = cv2.getTrackbarPos("threshold_green", "Parameters")
        t_blue = cv2.getTrackbarPos("threshold_blue", "Parameters")
        t_contrast = cv2.getTrackbarPos("threshold_contrast", "Parameters")
        t_light = cv2.getTrackbarPos("threshold_light", "Parameters")
        t_num_error = cv2.getTrackbarPos("threshold_num_error", "Parameters")
        t_dist = cv2.getTrackbarPos("threshold_dist", "Parameters")

        self.config = {
            "t_red": t_red,
            "t_green": t_green,
            "t_blue": t_blue,
            "t_contrast": t_contrast,
            "t_light": t_light,
            "t_num_error": t_num_error,
            "t_dist": t_dist
        }
        if TEST_MAMOS:
            if mm.output():
                self.snapshot("compare")

        ret, frame, _, mask = self.vid.get_frame(self.config, self.raw_data_draw)

        if ret:
            mask = imutils.resize(mask, height=int(cam_height / 2), width=int(cam_width / 2))
            mask = Image.fromarray(mask)
            self.tk_photo_line = ImageTk.PhotoImage(image=mask)
            self.canvas_rt.create_image(0, 0, image=self.tk_photo_line, anchor=tki.NW)
            if self.raw_data_draw:
                if t_dist != original_threshold_dist:
                    original_threshold_dist = t_dist
                    self.load_line(self.canvas2, self.raw_data_draw)
        self.window.after(self.delay, self.update)

    def reset(self):
        """Reset screen and parameters"""
        self.canvas2.delete("all")
        self.canvas3.delete("all")
        self.raw_data_draw = {"filename": ""}
        self.pathlabel.config(text="")
        self.count_draw_line = 0
        self.count_draw_sub_pol = 0

    def drawmode_default(self):
        self.btn_drawmode_detect = tki.Button(self.window, text="Detect", width=10, height=3,
                                              command=self.drawmode_detect)
        self.btn_drawmode_detect.place(relx=0.81, rely=0.15)
        self.btn_drawmode_area = tki.Button(self.window, text="Area", width=10, height=3, command=self.drawmode_area)
        self.btn_drawmode_area.place(relx=0.86, rely=0.15)
        self.btn_drawmode_ignore = tki.Button(self.window, text="Ignore", width=10, height=3,
                                              command=self.drawmode_ignore)
        self.btn_drawmode_ignore.place(relx=0.91, rely=0.15)

    def drawmode_detect(self):
        self.drawmode_default()
        self.btn_drawmode_detect = tki.Button(self.window, text="Detect", width=10, height=3,
                                              command=self.drawmode_detect, bg='green')
        self.btn_drawmode_detect.place(relx=0.81, rely=0.15)
        self.drawmode = "detect"

    def drawmode_area(self):
        self.drawmode_default()
        self.btn_drawmode_area = tki.Button(self.window, text="Area", width=10, height=3, command=self.drawmode_area,
                                            bg='red')
        self.btn_drawmode_area.place(relx=0.86, rely=0.15)
        self.drawmode = "area"

    def drawmode_ignore(self):
        self.drawmode_default()
        self.btn_drawmode_ignore = tki.Button(self.window, text="Ignore", width=10, height=3,
                                              command=self.drawmode_ignore, bg='blue')
        self.btn_drawmode_ignore.place(relx=0.91, rely=0.15)
        self.drawmode = "ignore"

    def on_button_press(self, event):
        x, y = event.x, event.y
        if self.start_x and self.start_y:
            if self.drawmode == "detect":
                self.count_draw_line += 1
                self.prev_line.append(
                    self.canvas2.create_line(x, y, self.start_x, self.start_y, width=original_threshold_dist,
                                             fill='green'))
                self.raw_data_draw[str(self.count_draw_line)] = {"rect": [self.start_x, self.start_y, x, y]}
                self.start_x, self.start_y = 0, 0
            else:
                if abs(x - self.start_x) < 20 and abs(y - self.start_y) < 20:
                    for draw_line in self.prev_sub_pol:
                        self.canvas2.delete(draw_line)
                    self.prev_sub_pol = []
                    self.count_draw_sub_pol = 0
                    flat_polygon = [item for sublist in self.polygon_data for item in sublist]
                    self.prev_pol = [self.canvas2.create_polygon(flat_polygon, outline='red', fill="", width=2)]

                    self.raw_data_draw[self.drawmode] = self.polygon_data
                    self.polygon_data = []
                    self.start_x, self.start_y = 0, 0
                else:
                    if self.drawmode == "area":
                        self.count_draw_sub_pol += 1
                        self.prev_sub_pol.append(
                            self.canvas2.create_line(x, y, self.polygon_data[-1][0], self.polygon_data[-1][1], width=2,
                                                     fill='red'))
                    else:
                        # todo
                        self.canvas2.create_line(x, y, self.polygon_data[-1][0], self.polygon_data[-1][1], width=2,
                                                 fill='blue')
                    self.polygon_data.append([x, y])
        else:
            self.start_x, self.start_y = x, y
            if self.drawmode != "detect":
                self.polygon_data.append([x, y])

    def undo(self, event):
        """Event right click on the canvas"""
        if self.count_draw_line:
            if self.drawmode == "detect":
                self.canvas2.delete(self.prev_line[-1])
                self.prev_line = self.prev_line[:-1]
                del self.raw_data_draw[str(self.count_draw_line)]
                self.count_draw_line -= 1

        if self.drawmode == "area":
            if self.prev_sub_pol:
                self.canvas2.delete(self.prev_sub_pol[-1])
                self.prev_sub_pol = self.prev_sub_pol[:-1]
                self.count_draw_sub_pol -= 1
                if self.polygon_data:
                    self.polygon_data = self.polygon_data[:-1]
                if len(self.polygon_data) == 1:
                    self.start_x, self.start_y = 0, 0
                    self.polygon_data = []
            else:
                if "area" in self.raw_data_draw:
                    del self.raw_data_draw["area"]
                    self.canvas2.delete(self.prev_sub_pol)
                    self.canvas2.delete(self.prev_pol)

    def snapshot(self, mode):
        """Take a photo"""
        # Get a frame from the video source
        start_task = time.time()
        ret, frame, contours, _ = self.vid.get_frame(self.config, self.raw_data_draw)

        end = time.time()
        print("Capture time: %f" % (end - start_task))
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        if ret:
            if mode == "original":
                self.file_path_o = out_path + "o_" + filename
                cv2.imwrite(self.file_path_o, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_o = Image.open(self.file_path_o)
                size = [cam_width, cam_height, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.tk_photo_org, anchor=tki.NW)
            elif mode == "compare":
                start = time.time()
                self.file_path_c = cp_path + "c_" + "temp_filename.jpg"
                cv2.imwrite(self.file_path_c, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_cp = Image.open(self.file_path_c)

                size = [cam_width, cam_height, 0, 0]
                self.load_img_cp = self.load_img_cp.resize((size[0], size[1]), Image.ANTIALIAS)
                error_cnt, error_lack = self.load_json_data(contours)
                if TEST_MAMOS:
                    if error_cnt:
                        mm.control(LED_NG)
                    else:
                        mm.control(LED_OK)
                end = time.time()
                print("Calculate time: %f" % (end - start))
                self.tk_photo_cp = ImageTk.PhotoImage(image=self.load_img_cp)
                self.canvas3.create_image(size[2], size[3], image=self.tk_photo_cp, anchor=tki.NW)
                if error_cnt:
                    for key in self.error_box:
                        self.canvas3.delete(self.error_box[key])
                    for i, cnt in enumerate(error_cnt):
                        polygon = [(cnt[0][0], cnt[0][1]), (cnt[1][0], cnt[0][1]), (cnt[1][0], cnt[1][1]),
                                   (cnt[0][0], cnt[1][1])]
                        self.error_box[i] = self.canvas3.create_polygon(polygon, outline='red', fill="", width=2)
                        self.canvas3.create_text((cnt[1][0] + 10, cnt[1][1]), text=i + 1, font=('Impact', -15),
                                                 fill="red")

                if error_lack:
                    width = fix_width()
                    for key in self.error_line:
                        self.canvas3.delete(self.error_line[key])
                    for i, lack_line in enumerate(error_lack):
                        if len(lack_line) > 2:
                            self.error_box[i] = self.canvas3.create_line(lack_line, fill='orange', width=width)
                            self.canvas3.create_text((lack_line[2] + 10, lack_line[3]), text=i + 1,
                                                     font=('Impact', -15),
                                                     fill="orange")
                        else:
                            self.canvas3.create_text((lack_line[0] + 10, lack_line[1]), text=i + 1,
                                                     font=('Impact', -15),
                                                     fill="orange")

                # self.load_rect(self.canvas3, self.raw_data_draw, cp_result)
                # self.raw_data_draw = {}
                end_task = time.time()
                print("Calculate event time: %f" % (end_task - start_task))

    def load_rect(self, cvs, data):
        """Load rectangle data from json"""
        for key, val in data.items():
            if key == "area":
                for i in range(1, len(val)):
                    cvs.create_line(val[i - 1][0], val[i - 1][1], val[i][0], val[i][1], width=2, fill='red')
                cvs.create_line(val[0][0], val[0][1], val[-1][0], val[-1][1], width=2, fill='red')
            elif key == "ignore":
                for i in range(3, len(val) + 1, 2):
                    cvs.create_line(val[i - 3], val[i - 2], val[i - 1], val[i], width=2, fill='blue')
            self.raw_data_draw[key] = val

    def load_line(self, cvs, data):
        """Load line data from json"""
        width = fix_width()
        for key, val in data.items():
            if key != "filename" and key != "area" and key != "ignore":
                if key in self.detect_line:
                    cvs.delete(self.detect_line[key])
                self.detect_line[key] = cvs.create_line(val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3],
                                                        width=width, fill='green')
                cvs.create_text((val["rect"][2] + 10, val["rect"][3]), text=key, font=('Impact', -15), fill="red")
            self.raw_data_draw[key] = val

    def snapshot_origin(self):
        """Call snapshot function with original image(LEFT)"""
        self.snapshot("original")

    def snapshot_compare(self):
        """Call snapshot function with compare image(RIGHT)"""
        self.snapshot("compare")

    def save_draw(self):
        if ("1" not in self.raw_data_draw) or ("area" not in self.raw_data_draw):
            msg_type = "Error"
            msg = "Need <draw> and <area> before <save>"
            messagebox.showerror(msg_type, msg)
            raise Exception(msg_type + ": " + msg)

        self.count_draw_line = 0
        copy_image = self.load_img_o.copy()
        for key, val in self.raw_data_draw.items():
            if key == "filename":
                self.raw_data_draw["filename"] = self.file_path_o
            elif key == "area" or key == "ignore":
                pass
            else:
                # start point = top-left
                x1, y1, x2, y2 = val["rect"]
                if (x1 > x2) and (y1 > y2):
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1
                image_area = copy_image.crop((x1, y1, x2, y2))
                if (image_area.size[0] != 0) and (image_area.size[1] != 0):
                    self.raw_data_draw[key]["rect"] = [x1, y1, x2, y2]

        # todo need test
        data = json.dumps(self.raw_data_draw)
        filename = 'data/data_%s.json' % self.file_path_o[:-4].replace("output/original/", "")
        with open(filename, 'w') as fp:
            fp.write(data)
        print("SAVE !", 'data/data_%s.json' % self.file_path_o[:-4].replace("output/original/", ""))
        self.raw_data_draw = {"filename": filename}
        self.reset()
        self.read_raw_data(filename)
        self.load_line(self.canvas2, self.raw_data_draw)

    def load_json_data(self, contours):
        """Load rectangle and filename data from json file"""
        if self.load_filename:
            with open(self.load_filename, 'r') as fp:
                self.raw_data_draw = json.load(fp)
        else:
            try:
                with open('data/data_%s.json' % self.file_path_o[:-4].replace("output/original/", ""), 'r') as fp:
                    self.raw_data_draw = json.load(fp)
            except Exception as e:
                print("ERROR: " + self.file_path_o)
                messagebox.showerror("Error", "Click <Save button> before <compare>")
                raise e
        return et.detect_error_cnt(contours, self.raw_data_draw, (t_dist * mini_sampling), t_num_error, t_dist)

    def read_raw_data(self, filename):
        """Read json data and update canvas"""
        if filename:
            with open(filename, 'r') as fp:
                self.raw_data_draw = json.load(fp)

                # load img
                print("Loading data: ")
                print(self.raw_data_draw)
                self.load_img_o = Image.open(self.raw_data_draw["filename"])
                self.file_path_o = self.raw_data_draw["filename"]
                size = [cam_width, cam_height, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.tk_photo_org, anchor=tki.NW)

                # load draw
                self.load_rect(self.canvas2, self.raw_data_draw)

    def browsefunc(self):
        """Find json data from Local PC"""
        self.load_filename = filedialog.askopenfilename()
        self.pathlabel.config(text=self.load_filename)
        self.read_raw_data(self.load_filename)


def exit_handler():
    print("Ending ..")
    if TEST_MAMOS:
        mm.clean()


atexit.register(exit_handler)
App(tki.Tk(), "Tkinter and OpenCV")
