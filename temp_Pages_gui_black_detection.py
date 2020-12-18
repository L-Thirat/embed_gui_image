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
import json
import glob
import os
import time
import atexit
import yaml

from src import extraction as et
from src.video_capture import MyVideoCapture as vc

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
    DEBUG = {"sample_img": 'test/test_lack2.png', "cam_width": cam_width,
             "cam_height": cam_height}  # Debug mode -> test from video source
    # DEBUG = {"sample_img": 'WIN_20201210_10_12_37_Pro.jpg', "cam_width": cam_width,
    #          "cam_height": cam_height}  # Debug mode -> test from video source
    TEST_MAMOS = False  # TEST MAMOS mode -> use Mamos's button instead GUI

    if TEST_MAMOS:
        from src.mamos import Mamos

        mm = Mamos(LED_OK, LED_NG, BTN_input)

original_threshold_dist = [0, 0]
mini_sampling = 4


def empty(area):
    pass


def fix_width(error_width=0):
    width = original_threshold_dist[1]
    if width > error_width:
        width -= error_width
    return width


# Create Control Bar
cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 800, 400)
cv2.createTrackbar("red", "Parameters", 255, 255, empty)
cv2.createTrackbar("green", "Parameters", 255, 255, empty)
cv2.createTrackbar("blue", "Parameters", 105, 255, empty)
cv2.createTrackbar("light", "Parameters", 0, 255, empty)
cv2.createTrackbar("contrast", "Parameters", 0, 255, empty)
cv2.createTrackbar("width min", "Parameters", 0, 100, empty)
cv2.createTrackbar("width max", "Parameters", 15, 100, empty)
cv2.createTrackbar("error %", "Parameters", 10, 100, empty)
cv2.createTrackbar("space", "Parameters", 15, 100, empty)


class Page(tki.Frame):
    def __init__(self, *args, **kwargs):
        window = self
        self.window = window
        tki.Frame.__init__(self, *args, **kwargs)

        # Load data
        self.config = None
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

        # open video source (by default this will try to open the computer webcam)
        self.vid = vc(DEBUG)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tki.Button(window, text="Snapshot", width=40, height=3, command=self.snapshot_origin)

        self.btn_save = tki.Button(window, text="Save", width=40, height=3, command=self.save_draw)

        self.load_filename = None
        self.browsebutton = tki.Button(window, text="Browse", width=20, height=3, command=self.browsefunc)

        self.btn_compare = tki.Button(window, text="Compare", width=40, height=3, command=self.snapshot_compare)

        self.btn_reset = tki.Button(window, text="Reset", width=40, height=3, command=self.reset)

        # 3 modes for draw
        self.btn_drawmode_detect = tki.Button(window, text="Detect", width=10, height=3, command=self.drawmode_detect,
                                              bg='green')
        self.btn_drawmode_area = tki.Button(window, text="Area", width=10, height=3, command=self.drawmode_area)
        self.btn_drawmode_ignore = tki.Button(window, text="Ignore", width=10, height=3, command=self.drawmode_ignore)

        self.pathlabel = tki.Label(window)

        # Create a canvas that can fit the above video source size
        # self.canvas_rt = tki.Canvas(self)
        # self.canvas_rt2 = tki.Canvas(self)

        self.canvas2 = tki.Canvas(window, cursor="cross")

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
        self.canvas3.config(width=cam_width, height=cam_height)

    def update(self, delay=15):
        global original_threshold_dist

        t_red = cv2.getTrackbarPos("red", "Parameters")
        t_green = cv2.getTrackbarPos("green", "Parameters")
        t_blue = cv2.getTrackbarPos("blue", "Parameters")
        t_contrast = cv2.getTrackbarPos("contrast", "Parameters")
        t_light = cv2.getTrackbarPos("light", "Parameters")
        t_num_error = cv2.getTrackbarPos("error %", "Parameters")
        t_width_min = cv2.getTrackbarPos("width min", "Parameters")
        t_width_max = cv2.getTrackbarPos("width max", "Parameters")
        t_space = cv2.getTrackbarPos("space", "Parameters")

        self.config = {
            "t_red": t_red,
            "t_green": t_green,
            "t_blue": t_blue,
            "t_contrast": t_contrast,
            "t_light": t_light,
            "t_num_error": t_num_error,
            "t_width_min": t_width_min,
            "t_width_max": t_width_max,
            "t_space": t_space
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
                if (t_width_min, t_width_max) != original_threshold_dist:
                    original_threshold_dist = (t_width_min, t_width_max)
                    self.load_line(self.canvas2, self.raw_data_draw)

        self.window.after(delay, self.update)

    def update2(self, delay=15):
        self.config = {"t_red": 255, "t_green": 255, "t_blue": 255, "t_contrast": 0, "t_light": 0}
        ret, frame, _, mask = self.vid.get_frame(self.config, self.raw_data_draw)
        if ret:
            mask = imutils.resize(mask, height=int(cam_height / 2), width=int(cam_width / 2))
            mask = Image.fromarray(mask)
            self.tk_photo_line = ImageTk.PhotoImage(image=mask)
            self.canvas_rt2.create_image(0, 0, image=self.tk_photo_line, anchor=tki.NW)

        self.window.after(delay, self.update2)

    def reset(self):
        """Reset screen and parameters"""
        self.canvas2.delete("all")
        self.canvas3.delete("all")
        self.raw_data_draw = {"filename": ""}
        self.file_path_o = ""
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
                    self.canvas2.create_line(x, y, self.start_x, self.start_y, width=original_threshold_dist[1],
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
                if not contours:
                    msg_type = "ERROR"
                    msg = "No detect line"
                    messagebox.showerror(msg_type, msg)
                    raise msg_type + ": " + msg
                error_cnt, error_lack = self.get_result(contours)
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

    def get_result(self, contours):
        """Load rectangle and filename data from json file"""
        if self.load_filename:
            with open(self.load_filename, 'r') as fp:
                self.raw_data_draw = json.load(fp)
        else:
            try:
                with open('data/data_%s.json' % self.file_path_o[:-4].replace("output/original/", ""), 'r') as fp:
                    self.raw_data_draw = json.load(fp)
            except Exception as e:
                msg_type = "Error"
                msg = "Click <Save button> before <compare>"
                raise Exception(msg_type + ": " + msg)
        error_cnt, error_lack = et.detect_error_cnt(contours, self.raw_data_draw,
                                                    (mini_sampling * self.config["t_width_max"]), self.config)
        if TEST_MAMOS:
            if error_cnt or error_lack:
                mm.control(LED_NG)
            else:
                mm.control(LED_OK)
        return error_cnt, error_lack

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
        self.reset()
        self.read_raw_data(self.load_filename)
        self.load_line(self.canvas2, self.raw_data_draw)

    def show(self):
        self.lift()


class Page1(Page):
    def __init__(self, run_page, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.run_page1 = True
        # self.canvas_rt.place(relx=0.01, rely=0.05)
        # self.canvas_rt.config(width=cam_width * 0.5, height=cam_height * 0.5)
        # self.setting = tki.Button(self, text="Setting", width=20, height=3, command=self.go_setting)

        self.btn_snapshot.place(relx=0.41, rely=0.05)
        self.btn_save.place(relx=0.61, rely=0.05)
        self.browsebutton.place(relx=0.81, rely=0.05)
        # self.setting.place(relx=0.91, rely=0.05)
        self.btn_compare.place(relx=0.41, rely=0.15)
        self.btn_reset.place(relx=0.61, rely=0.15)
        self.btn_drawmode_detect.place(relx=0.81, rely=0.15)
        self.btn_drawmode_area.place(relx=0.86, rely=0.15)
        self.btn_drawmode_ignore.place(relx=0.91, rely=0.15)
        self.pathlabel.place(relx=0.41, rely=0.25)
        self.canvas2.place(relx=0.1, rely=0.4)
        self.canvas3.place(relx=0.5, rely=0.4)

        # # # After it is called once, the update method will be automatically called every delay milliseconds
        if run_page:
            self.update()
            print(1)


class Page2(Page):
    def __init__(self, run_page, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        # self.canvas_rt2.place(relx=0.01, rely=0.05)
        # self.canvas_rt2.config(width=cam_width * 0.5, height=cam_height * 0.5)
        lbl_topic = tki.Label(self, text="Colour", font=("Courier", 55))
        lbl_topic.place(relx=0.01, rely=0.61)
        lbl_red = tki.Label(self, text="Red", font=("Courier", 44))
        lbl_red.place(relx=0.01, rely=0.71)
        pad_half_width = 300
        scale_red = tki.Scale(self, from_=0, to=255, tickinterval=51, orient=tki.HORIZONTAL, length=(self.winfo_screenwidth()/2)-pad_half_width)
        scale_red.place(relx=0.1, rely=0.71)
        config = {"anc": "asd"}

        # # # After it is called once, the update method will be automatically called every delay milliseconds
        # if run_page:
        #     print(2)
        #     self.update2()


class App(tki.Frame):
    def __init__(self, window, window_title, *args, **kwargs):
        self.window = window
        tki.Frame.__init__(self, *args, **kwargs)

        buttonframe = tki.Frame(self)
        container = tki.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="bottom", fill="both", expand=True)

        self.canvas_rt = tki.Canvas(self)
        self.canvas_rt.place(relx=0.01, rely=0.05)
        self.canvas_rt.config(width=cam_width * 0.5, height=cam_height * 0.5)

        self.p1 = Page1(True, self)
        self.p2 = Page2(False, self)
        self.p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tki.Button(buttonframe, text="Page 1", command=self.p1.lift)
        b2 = tki.Button(buttonframe, text="Page 2", command=self.go_page2)
        b1.pack(side="left")
        b2.pack(side="left")
        self.p1.show()

    def go_page2(self):
        self.p1 = Page1(False, self)
        self.p2 = Page2(True, self)
        self.p2.show()


def exit_handler():
    print("Ending ..")
    if TEST_MAMOS:
        mm.clean()


def toggle_geom(self, event):
    geom = self.master.winfo_geometry()
    print(geom, self._geom)
    self.master.geometry(self._geom)
    self._geom = geom


if __name__ == "__main__":
    atexit.register(exit_handler)

    root = tki.Tk()
    main = App(root, "Tkinter and OpenCV")
    main.pack(side="top", fill="both", expand=True)

    # Tkinter setting
    pad = 3
    tki.Frame._geom = '200x200+0+0'
    root.geometry("{0}x{1}+0+0".format(
        root.winfo_screenwidth() - pad, root.winfo_screenheight() - pad))
    root.bind('<Escape>', toggle_geom)
    root.title("Tkinter and OpenCV")
    root.resizable(1, 1)
    root.configure(background="#d9d9d9")
    root.mainloop()
