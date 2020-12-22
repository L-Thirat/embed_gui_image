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
import io

import init_project

init_project.create_folders()

from src import extraction as et
from src import linear_processing as lp
from src.video_capture import MyVideoCapture as vc
from src import logger

from PIL import EpsImagePlugin

log = logger.GetSystemLogger()

# Setting
with open(r'setting.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    setting_data = yaml.load(file, Loader=yaml.FullLoader)

    cam_height = int(setting_data["cam_height"])
    cam_width = int(setting_data["cam_width"])
    out_path = setting_data["out_path"]
    cp_path = setting_data["cp_path"]
    LED_OK = setting_data["LED_OK"]
    LED_NG = setting_data["LED_NG"]
    BTN_input = setting_data["BTN_INPUT"]

    # Testing
    DEBUG = setting_data["DEBUG"]
    if "sample_img" in DEBUG:
        DEBUG["cam_width"] = cam_width
        DEBUG["cam_height"] = cam_height
    TEST_MAMOS = bool(setting_data["TEST_MAMOS"])
    # DEBUG = {"sample_img": 'test/rgb.jpg', "cam_width": cam_width,
    #          "cam_height": cam_height}  # Debug mode -> test from video source
    # DEBUG = {"sample_img": 'WIN_20201210_10_12_37_Pro.jpg', "cam_width": cam_width,
    #          "cam_height": cam_height}  # Debug mode -> test from video source
    # DEBUG = {}
    # TEST_MAMOS = False  # TEST MAMOS mode -> use Mamos's button instead GUI

    if TEST_MAMOS:
        from src.mamos import Mamos

        mm = Mamos(LED_OK, LED_NG, BTN_input)
    else:
        EpsImagePlugin.gs_windows_binary = setting_data["gs"]

original_threshold_dist = [0, 0]
mini_sampling = 4


def empty(area):
    pass


def fix_width(error_width=0):
    width = original_threshold_dist[1]
    if width > error_width:
        width -= error_width
    return width


class Page(tki.Frame):
    def __init__(self, *args, **kwargs):
        tki.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class Page1(Page):
    def __init__(self, app, *args, **kwargs):
        self.vid = app.vid
        self.config = app.config
        self.window = self

        Page.__init__(self, *args, **kwargs)

        # Load data
        self.file_path_o = ""
        self.file_path_c = ""
        self.tk_photo_line = None
        self.tk_photo_org = None
        self.tk_photo_cp = None
        self.load_img_o = None
        self.load_img_cp = None
        self.load_filename = None
        self.raw_data_draw = {"filename": ""}

        # Visualize output
        self.contour = []
        self.detect_line = {}
        self.error_box = {}
        self.error_line = {}

        buttonframe = tki.Frame(self)
        buttonframe.pack(side="top", fill="both", expand=True)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tki.Button(buttonframe, text="Snapshot", font=("Courier", 44), width=9,
                                       command=self.snapshot_origin)
        self.btn_snapshot.place(relx=0.38, rely=0.05)

        self.btn_save = tki.Button(buttonframe, text="Save", font=("Courier", 44), width=9, command=self.save_draw)
        self.btn_save.place(relx=0.56, rely=0.05)

        self.browsebutton = tki.Button(buttonframe, text="Browse", font=("Courier", 44), width=9,
                                       command=self.browsefunc)
        self.browsebutton.place(relx=0.74, rely=0.05)

        self.btn_compare = tki.Button(buttonframe, text="Compare", font=("Courier", 44), width=9,
                                      command=self.snapshot_compare)
        self.btn_compare.place(relx=0.38, rely=0.18)

        self.btn_reset = tki.Button(buttonframe, text="Reset", font=("Courier", 44), width=9, command=self.reset)
        self.btn_reset.place(relx=0.56, rely=0.18)

        self.btn_drawmode_detect = tki.Button(buttonframe, text="Detect", font=("Courier", 44),
                                              command=self.drawmode_detect,
                                              bg='green')
        self.btn_drawmode_detect.place(relx=0.74, rely=0.18)
        self.btn_drawmode_area = tki.Button(buttonframe, text="Area", font=("Courier", 44), command=self.drawmode_area)
        self.btn_drawmode_area.place(relx=0.88, rely=0.18)
        # todo ignore modes for draw
        # self.btn_drawmode_ignore = tki.Button(buttonframe, text="Ignore", font=("Courier", 44), width=3, height=3,
        #                                       command=self.drawmode_ignore)
        # self.btn_drawmode_ignore.place(relx=0.91, rely=0.15)

        # todo remove or use ?
        self.pathlabel = tki.Label(buttonframe)
        self.pathlabel.place(relx=0.41, rely=0.25)

        # Result
        lbl_result = tki.Label(buttonframe, text="Result", font=("Courier", 44))
        lbl_result.place(relx=0.83, rely=0.35)
        self.lbl_result = tki.Label(buttonframe, text="        ", bg="yellow", font=("Courier", 44))
        self.lbl_result.place(relx=0.83, rely=0.44)

        # Drawing cv
        self.canvas2 = tki.Canvas(buttonframe, cursor="cross")
        self.canvas2.place(relx=0.05, rely=0.35)
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

        self.canvas3 = tki.Canvas(buttonframe)
        self.canvas3.place(relx=0.45, rely=0.35)
        self.canvas3.config(width=cam_width, height=cam_height)

    def reset(self):
        """Reset screen and parameters"""
        self.canvas2.delete("all")
        self.canvas3.delete("all")
        self.raw_data_draw = {"filename": ""}
        self.file_path_o = ""
        self.pathlabel.config(text="")
        self.lbl_result.config(text="        ", bg="yellow")
        self.count_draw_line = 0
        self.count_draw_sub_pol = 0

    def drawmode_default(self):
        self.btn_drawmode_detect = tki.Button(self.window, text="Detect", font=("Courier", 44),
                                              command=self.drawmode_detect)
        self.btn_drawmode_detect.place(relx=0.74, rely=0.18)
        self.btn_drawmode_area = tki.Button(self.window, text="Area", font=("Courier", 44), command=self.drawmode_area)
        self.btn_drawmode_area.place(relx=0.88, rely=0.18)
        # self.btn_drawmode_ignore = tki.Button(self.window, text="Ignore", width=10, height=3,
        #                                       command=self.drawmode_ignore)
        # self.btn_drawmode_ignore.place(relx=0.91, rely=0.15)

    def drawmode_detect(self):
        self.drawmode_default()
        self.btn_drawmode_detect = tki.Button(self.window, text="Detect", font=("Courier", 44),
                                              command=self.drawmode_detect, bg='green')
        self.btn_drawmode_detect.place(relx=0.74, rely=0.18)
        self.drawmode = "detect"

    def drawmode_area(self):
        self.drawmode_default()
        self.btn_drawmode_area = tki.Button(self.window, text="Area", font=("Courier", 44), command=self.drawmode_area,
                                            bg='red')
        self.btn_drawmode_area.place(relx=0.88, rely=0.18)
        self.drawmode = "area"

    # def drawmode_ignore(self):
    #     self.drawmode_default()
    #     self.btn_drawmode_ignore = tki.Button(self.window, text="Ignore", width=10, height=3,
    #                                           command=self.drawmode_ignore, bg='blue')
    #     self.btn_drawmode_ignore.place(relx=0.91, rely=0.15)
    #     self.drawmode = "ignore"

    def on_button_press(self, event):
        x, y = event.x, event.y
        if self.start_x and self.start_y:
            if self.drawmode == "detect":
                self.count_draw_line += 1
                x1, y1, x2, y2 = lp.length2points((x, y), (self.start_x, self.start_y),
                                                  original_threshold_dist[1])
                self.prev_line.append(
                    self.canvas2.create_line(x1, y1, x2, y2, width=original_threshold_dist[1],
                                             fill='green'))
                if self.start_x < x:
                    green_line = {"rect": [self.start_x, self.start_y, x, y]}
                else:
                    green_line = {"rect": [x, y, self.start_x, self.start_y]}
                self.raw_data_draw[str(self.count_draw_line)] = green_line
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
                error_over, error_under = self.get_result(contours)
                end = time.time()
                print("Calculate time: %f" % (end - start))
                self.tk_photo_cp = ImageTk.PhotoImage(image=self.load_img_cp)
                self.canvas3.create_image(size[2], size[3], image=self.tk_photo_cp, anchor=tki.NW)
                output_status = "        "
                if error_over:
                    output_status = "NG:OVER"
                    for key in self.error_box:
                        self.canvas3.delete(self.error_box[key])
                    for i, cnt in enumerate(error_over):
                        polygon = [(cnt[0][0], cnt[0][1]), (cnt[1][0], cnt[0][1]), (cnt[1][0], cnt[1][1]),
                                   (cnt[0][0], cnt[1][1])]
                        self.error_box[i] = self.canvas3.create_polygon(polygon, outline='red', fill="", width=2)
                        self.canvas3.create_text((cnt[1][0] + 10, cnt[1][1]), text=i + 1, font=('Impact', -15),
                                                 fill="red")

                if error_under:
                    if output_status == "NG:OVER":
                        output_status = "NG:BOTH"
                    else:
                        output_status = "NG:UNDER"
                    width = fix_width()
                    for key in self.error_line:
                        self.canvas3.delete(self.error_line[key])
                    for i, lack_line in enumerate(error_under):
                        if len(lack_line) > 2:
                            self.error_box[i] = self.canvas3.create_line(lack_line, fill='orange', width=width)
                            self.canvas3.create_text((lack_line[2] + 10, lack_line[3]), text=i + 1,
                                                     font=('Impact', -15),
                                                     fill="orange")
                        else:
                            self.canvas3.create_text((lack_line[0] + 10, lack_line[1]), text=i + 1,
                                                     font=('Impact', -15),
                                                     fill="orange")

                if not error_under and not error_over:
                    output_status = "OK"

                # self.load_rect(self.canvas3, self.raw_data_draw, cp_result)
                # self.raw_data_draw = {}

                # Output Screen
                if output_status == "OK":
                    self.lbl_result.config(text=output_status, bg="green")
                else:
                    self.lbl_result.config(text=output_status, bg="red")

                # Output log
                cur_time = datetime.datetime.now()
                file_time_form = cur_time.strftime("%Y%m%d_%H%M%S")
                log_time_form = cur_time.strftime("%Y:%m:%d %H:%M:%S")
                msg = log_time_form + "> Output: " + output_status + " | Over count: %d | Under count:  %d" % (
                len(error_over), len(error_under))
                log.info(msg)

                # use PIL to convert  PS to PNG
                self.canvas3.update()
                if output_status == "OK":
                    filename = cp_path + file_time_form + "_" + "OK"
                else:
                    filename = cp_path + file_time_form + "_" + "NG"
                filename_png = filename + ".png"
                ps = self.canvas3.postscript(colormode='color')
                img = Image.open(io.BytesIO(ps.encode('utf-8')))
                img.save(filename_png)

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
                x1, y1, x2, y2 = lp.length2points((val["rect"][0], val["rect"][1]), (val["rect"][2], val["rect"][3]),
                                                  width)
                self.detect_line[key] = cvs.create_line(x1, y1, x2, y2, width=width, fill='green')
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

        # save setting image
        # use PIL to convert  PS to PNG
        self.canvas2.update()
        filename_png = self.file_path_o.replace("/o_", "/s_")
        ps = self.canvas2.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img.save(filename_png)

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
                pass
                # todo test 1 pin
                # mm.control(LED_OK)
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


class Page2(Page):
    def __init__(self, app, *args, **kwargs):
        self.app = app
        Page.__init__(self, *args, **kwargs)
        self.buttonframe = tki.Frame(self)
        self.buttonframe.pack(side="top", fill="both", expand=True)

        # Camera Tab
        lbl_topic = tki.Label(self.buttonframe, text="Camera", font=("Courier", 55))
        lbl_topic.place(relx=0.61, rely=0.01)
        pad_half_width = 500

        lbl_light = tki.Label(self.buttonframe, text="Light", font=("Courier", 44))
        lbl_light.place(relx=0.47, rely=0.11)
        scale_light = tki.Scale(self.buttonframe, from_=-255, to=255, tickinterval=51, orient=tki.HORIZONTAL,
                                length=(self.winfo_screenwidth() * 0.5 - pad_half_width), command=self.change_light)
        scale_light.set(self.app.config["t_light"])
        scale_light.place(relx=0.65, rely=0.11)

        lbl_contrast = tki.Label(self.buttonframe, text="Contrast", font=("Courier", 44))
        lbl_contrast.place(relx=0.47, rely=0.21)
        scale_contrast = tki.Scale(self.buttonframe, from_=-255, to=255, tickinterval=51, orient=tki.HORIZONTAL,
                                   length=(self.winfo_screenwidth() * 0.5 - pad_half_width),
                                   command=self.change_contrast)
        scale_contrast.set(self.app.config["t_contrast"])
        scale_contrast.place(relx=0.65, rely=0.21)

        lbl_zoom = tki.Label(self.buttonframe, text="Zoom", font=("Courier", 44))
        lbl_zoom.place(relx=0.47, rely=0.31)
        scale_zoom = tki.Scale(self.buttonframe, from_=1, to=4, tickinterval=1, orient=tki.HORIZONTAL,
                               length=(self.winfo_screenwidth() * 0.5 - pad_half_width), command=self.change_zoom)
        scale_zoom.set(self.app.config["t_zoom"])
        scale_zoom.place(relx=0.65, rely=0.31)

        # Colour tab
        lbl_topic = tki.Label(self.buttonframe, text="Colour", font=("Courier", 55))
        lbl_topic.place(relx=0.15, rely=0.40)

        lbl_red = tki.Label(self.buttonframe, text="Red", font=("Courier", 44))
        lbl_red.place(relx=0.01, rely=0.5)
        scale_red = tki.Scale(self.buttonframe, from_=0, to=255, tickinterval=51, orient=tki.HORIZONTAL,
                              length=(self.winfo_screenwidth() * 0.5) - pad_half_width, command=self.change_red)
        scale_red.set(self.app.config["t_red"])
        scale_red.place(relx=0.12, rely=0.5)

        lbl_green = tki.Label(self.buttonframe, text="Green", font=("Courier", 44))
        lbl_green.place(relx=0.01, rely=0.6)
        scale_green = tki.Scale(self.buttonframe, from_=0, to=255, tickinterval=51, orient=tki.HORIZONTAL,
                                length=(self.winfo_screenwidth() * 0.5) - pad_half_width, command=self.change_green)
        scale_green.set(self.app.config["t_green"])
        scale_green.place(relx=0.12, rely=0.6)

        lbl_blue = tki.Label(self.buttonframe, text="Blue", font=("Courier", 44))
        lbl_blue.place(relx=0.01, rely=0.7)
        scale_blue = tki.Scale(self.buttonframe, from_=0, to=255, tickinterval=51, orient=tki.HORIZONTAL,
                               length=(self.winfo_screenwidth() * 0.5) - pad_half_width, command=self.change_blue)
        scale_blue.set(self.app.config["t_blue"])
        scale_blue.place(relx=0.12, rely=0.7)

        # Detection tab
        lbl_topic = tki.Label(self.buttonframe, text="Detection", font=("Courier", 55))
        lbl_topic.place(relx=0.57, rely=0.40)

        lbl_space = tki.Label(self.buttonframe, text="Space", font=("Courier", 44))
        lbl_space.place(relx=0.47, rely=0.5)
        scale_space = tki.Scale(self.buttonframe, from_=0, to=cam_width, tickinterval=cam_width / 10,
                                orient=tki.HORIZONTAL,
                                length=(self.winfo_screenwidth() * 0.5) - pad_half_width, command=self.change_space)
        scale_space.set(self.app.config["t_space"])
        scale_space.place(relx=0.65, rely=0.5)

        lbl_error = tki.Label(self.buttonframe, text="Error %", font=("Courier", 44))
        lbl_error.place(relx=0.47, rely=0.6)
        scale_error = tki.Scale(self.buttonframe, from_=0, to=100, tickinterval=20, orient=tki.HORIZONTAL,
                                length=(self.winfo_screenwidth() * 0.5) - pad_half_width, command=self.change_error)
        scale_error.set(self.app.config["t_error"])
        scale_error.place(relx=0.65, rely=0.6)

        lbl_min = tki.Label(self.buttonframe, text="Width", font=("Courier", 44))
        lbl_min.place(relx=0.47, rely=0.7)
        scale_min = tki.Scale(self.buttonframe, from_=0, to=50, tickinterval=10, orient=tki.HORIZONTAL,
                              length=(self.winfo_screenwidth() * 0.14), command=self.change_min)
        scale_min.set(self.app.config["t_width_min"])
        scale_min.place(relx=0.58, rely=0.7)

        lbl_max = tki.Label(self.buttonframe, text="~", font=("Courier", 44))
        lbl_max.place(relx=0.73, rely=0.7)
        scale_max = tki.Scale(self.buttonframe, from_=0, to=50, tickinterval=10, orient=tki.HORIZONTAL,
                              length=(self.winfo_screenwidth() * 0.14), command=self.change_max)
        scale_max.set(self.app.config["t_width_max"])
        scale_max.place(relx=0.753, rely=0.7)

        btn_save = tki.Button(self.buttonframe, font=("Courier", 44), text="Save", command=self.save_config)
        btn_save.place(relx=0.45, rely=0.8)

    def save_config(self):
        with open('config.yaml', 'w') as outfile:
            yaml.dump(self.app.config, outfile, default_flow_style=False)

    def change_red(self, val):
        self.app.config["t_red"] = int(val)

    def change_green(self, val):
        self.app.config["t_green"] = int(val)

    def change_blue(self, val):
        self.app.config["t_blue"] = int(val)

    def change_light(self, val):
        self.app.config["t_light"] = int(val)

    def change_contrast(self, val):
        self.app.config["t_contrast"] = int(val)

    def change_zoom(self, val):
        self.app.config["t_zoom"] = int(val)

    def change_space(self, val):
        self.app.config["t_space"] = int(val)

    def change_error(self, val):
        self.app.config["t_error"] = int(val)

    def change_min(self, val):
        self.app.config["t_width_min"] = int(val)

    def change_max(self, val):
        self.app.config["t_width_max"] = int(val)


class App(tki.Frame):
    def __init__(self, window, window_title, *args, **kwargs):
        self.this = self
        self.window = window
        self.vid = vc(DEBUG)

        with open(r'config.yaml') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            self.this.config = yaml.load(file, Loader=yaml.FullLoader)

        tki.Frame.__init__(self, *args, **kwargs)
        # open video source (by default this will try to open the computer webcam)

        buttonframe = tki.Frame(self)
        container = tki.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        self.p1 = Page1(self.this, self)
        self.p2 = Page2(self.this, self)

        self.p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tki.Button(buttonframe, text="Home", font=("Courier", 44), command=self.p1.lift)
        b2 = tki.Button(buttonframe, text="Setting", font=("Courier", 44), command=self.p2.lift)

        b1.pack(side="right")
        b2.pack(side="right")

        # Create a canvas that can fit the above video source size
        self.canvas_rt = tki.Canvas(window)
        self.canvas_rt.place(relx=0.05, rely=0.01)
        self.canvas_rt.config(width=int(cam_width * 0.8), height=int(cam_height * 0.8))

        # # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        self.p1.show()

    def update(self):
        global original_threshold_dist

        if TEST_MAMOS:
            if mm.output():
                self.p1.snapshot("compare")

        ret, frame, _, mask = self.vid.get_frame(self.this.config, self.p1.raw_data_draw)
        if ret:
            mask = imutils.resize(mask, height=int(cam_height * 0.8), width=int(cam_width * 0.8))
            mask = Image.fromarray(mask)
            self.p1.tk_photo_line = ImageTk.PhotoImage(image=mask)
            self.canvas_rt.create_image(0, 0, image=self.p1.tk_photo_line, anchor=tki.NW)
            if self.p1.raw_data_draw:
                if (self.this.config["t_width_min"], self.this.config["t_width_max"]) != original_threshold_dist:
                    original_threshold_dist = (self.this.config["t_width_min"], self.this.config["t_width_max"])
                    self.p1.load_line(self.p1.canvas2, self.p1.raw_data_draw)
        self.window.after(self.delay, self.update)


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
