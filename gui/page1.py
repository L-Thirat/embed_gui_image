from typing import Dict, List, Any

import tkinter as tki
from tkinter import filedialog
from tkinter import messagebox

import cv2
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import datetime
import json
import glob
import os
import time
import io

from src import extraction as et
from src import linear_processing as lp
from gui.page_control import Page


class Page1(Page):
    raw_data_draw = ...  # type: Dict["filename":str, "area":List[str, List[Any]], "draws":Dict[List[int]]]

    def __init__(self, app, *args, **kwargs):
        self.vid = app.vid
        self.config = app.config
        self.window = self
        self.app = app

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
        self.raw_data_draw = {
            "filename": "",
            "area": [],
            "draws": {},
        }

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
                                       command=self.browse)
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
        self.canvas2.config(width=app.cam_width, height=app.cam_height)
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
        self.canvas3.config(width=app.cam_width, height=app.cam_height)

    def reset(self):
        """Reset screen and parameters"""
        self.canvas2.delete("all")
        self.canvas3.delete("all")
        self.raw_data_draw = {
            "filename": "",
            "area": [],
            "draws": {}
        }
        self.app.range_rgb = [{
            "point": None,
            "min": [255, 255, 255],
            "max": [0, 0, 0]
        }]
        self.app.undo_rgb(None)

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
                                                  self.app.original_threshold_dist[1])
                self.prev_line.append(
                    self.canvas2.create_line(x1, y1, x2, y2, width=self.app.original_threshold_dist[1],
                                             fill='green'))
                if self.start_x < x:
                    green_line = [self.start_x, self.start_y, x, y]
                else:
                    green_line = [x, y, self.start_x, self.start_y]
                self.raw_data_draw["draws"][str(self.count_draw_line)] = green_line
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
                    # else:
                    #     # todo
                    #     self.canvas2.create_line(x, y, self.polygon_data[-1][0], self.polygon_data[-1][1], width=2,
                    #                              fill='blue')
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
                del self.prev_line[-1]
                del self.raw_data_draw["draws"][str(self.count_draw_line)]
                self.count_draw_line -= 1

        if self.drawmode == "area":
            if self.prev_sub_pol:
                self.canvas2.delete(self.prev_sub_pol[-1])
                del self.prev_sub_pol[-1]
                self.count_draw_sub_pol -= 1
                if self.polygon_data:
                    del self.polygon_data[-1]
                if len(self.polygon_data) == 1:
                    self.start_x, self.start_y = 0, 0
                    self.polygon_data = []
            else:
                if "area" in self.raw_data_draw:
                    self.raw_data_draw["area"] = []
                    self.canvas2.delete(self.prev_sub_pol)
                    self.canvas2.delete(self.prev_pol)

    def snapshot(self, mode):
        """Get a frame from the video source"""
        start_task = time.time()
        ret, frame, contours, _ = self.vid.get_frame(self.config, self.raw_data_draw)

        end = time.time()
        print("Capture time: %f" % (end - start_task))
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        if ret:
            if mode == "original":
                self.file_path_o = self.app.out_path + "o_" + filename
                cv2.imwrite(self.file_path_o, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_o = Image.open(self.file_path_o)
                size = [self.app.cam_width, self.app.cam_height, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.tk_photo_org, anchor=tki.NW)

            elif mode == "compare":
                start = time.time()
                self.file_path_c = self.app.cp_path + "c_" + "temp_filename.jpg"
                cv2.imwrite(self.file_path_c, cv2.cvtColor(self.app.frame, cv2.COLOR_RGB2BGR))
                self.load_img_cp = Image.open(self.file_path_c)

                size = [self.app.cam_width, self.app.cam_height, 0, 0]
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
                    width = self.app.original_threshold_dist[1]
                    for key in self.error_line:
                        self.canvas3.delete(self.error_line[key])
                    for i, lack_line in enumerate(error_under):
                        if len(lack_line) > 2:
                            self.error_box[i] = self.canvas3.create_line(lack_line, fill='orange', width=width)
                            self.canvas3.create_text((lack_line[2] + 10, lack_line[3]), text=i + 1,
                                                     font=('Impact', -15),
                                                     fill="orange")
                        elif len(lack_line) == 2:
                            self.canvas3.create_text((lack_line[0] + 10, lack_line[1]), text=i + 1,
                                                     font=('Impact', -15),
                                                     fill="orange")

                if not error_under and not error_over:
                    output_status = "OK"

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
                self.app.log.info(msg)

                # use PIL to convert  PS to PNG
                self.canvas3.update()
                if output_status == "OK":
                    filename = self.app.cp_path + file_time_form + "_" + "OK"
                else:
                    filename = self.app.cp_path + file_time_form + "_" + "NG"
                filename_png = filename + ".png"
                ps = self.canvas3.postscript(colormode='color')
                img = Image.open(io.BytesIO(ps.encode('utf-8')))
                img.save(filename_png)

                end_task = time.time()
                print("Calculate event time: %f" % (end_task - start_task))

    def load_rect(self, cvs):
        """Load rectangle data from json"""
        val = self.raw_data_draw["area"]
        for i in range(1, len(val)):
            cvs.create_line(val[i - 1][0], val[i - 1][1], val[i][0], val[i][1], width=2, fill='red')
        cvs.create_line(val[0][0], val[0][1], val[-1][0], val[-1][1], width=2, fill='red')
        # elif key == "ignore":
        #     for i in range(3, len(val) + 1, 2):
        #         cvs.create_line(val[i - 3], val[i - 2], val[i - 1], val[i], width=2, fill='blue')

    def load_line(self, cvs):
        """Load line data from json"""
        width = self.app.original_threshold_dist[1]
        for key, val in self.raw_data_draw["draws"].items():
            if key in self.detect_line:
                cvs.delete(self.detect_line[key])
            x1, y1, x2, y2 = lp.length2points((val[0], val[1]), (val[2], val[3]), width)
            self.detect_line[key] = cvs.create_line(x1, y1, x2, y2, width=width, fill='green')
            cvs.create_text((val[2] + 10, val[3]), text=key, font=('Impact', -15), fill="red")

    def snapshot_origin(self):
        """Call snapshot function with original image(LEFT)"""
        self.snapshot("original")

    def snapshot_compare(self):
        """Call snapshot function with compare image(RIGHT)"""
        self.snapshot("compare")

    def save_draw(self):
        if (not self.raw_data_draw["draws"]) or (not self.raw_data_draw["area"]):
            msg_type = "Error"
            msg = "Need <draw> and <area> before <save>"
            messagebox.showerror(msg_type, msg)
            raise Exception(msg_type + ": " + msg)

        self.count_draw_line = 0
        copy_image = self.load_img_o.copy()

        self.raw_data_draw["filename"] = self.file_path_o
        for n in self.raw_data_draw["draws"]:
            # todo *start point = from left + (top) passed?
            [x1, y1, x2, y2] = self.raw_data_draw["draws"][n]
            if x2 < x1:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            elif x2 == x1:
                if y2 > y1:
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1
            image_area = copy_image.crop((x1, y1, x2, y2))
            if (image_area.size[0] != 0) and (image_area.size[1] != 0):
                self.raw_data_draw["draws"][n] = [x1, y1, x2, y2]

        # Save setting data
        data = json.dumps(self.raw_data_draw)
        filename = 'data/data_%s.json' % self.file_path_o[:-4].replace("output/original/", "")
        with open(filename, 'w') as fp:
            fp.write(data)
        print("SAVE !", 'data/data_%s.json' % self.file_path_o[:-4].replace("output/original/", ""))
        self.raw_data_draw = {
            "filename": filename,
            "area": [],
            "draws": {}
        }
        self.reset()
        self.read_raw_data(filename)
        self.load_line(self.canvas2)

        # Save setting image
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
            except Exception:
                msg_type = "Error"
                msg = "Click <Save button> before <compare>"
                raise Exception(msg_type + ": " + msg)
        error_cnt, error_lack = et.detect_error_cnt(contours, self.raw_data_draw, self.config)
        if self.app.TEST_MAMOS:
            if error_cnt or error_lack:
                self.app.mm.control(self.app.LED_NG)
            else:
                self.app.mm.control(self.app.LED_OK)
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
                size = [self.app.cam_width, self.app.cam_height, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.tk_photo_org, anchor=tki.NW)

                # load draw
                self.load_rect(self.canvas2)

    def browse(self):
        """Find json data from Local PC"""
        self.load_filename = filedialog.askopenfilename()
        self.pathlabel.config(text=self.load_filename)
        self.reset()
        self.read_raw_data(self.load_filename)
        self.load_line(self.canvas2)
