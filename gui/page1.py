from gui.page_control import Page
import tkinter as tki

from typing import Dict, List, Any

from tkinter import filedialog
from tkinter import messagebox

import copy
import cv2
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import datetime
import json
import glob
import os
import time
import io

from src.video_capture import MyVideoCapture as Vdo
from src import extraction as et
from gui.page_control import Page
from gui.drawing_control import DrawingPage
import init_project
from init_project import init_dir

# from gui import Page1

# Load init params
init_param = init_project.init_param()


class Page1(DrawingPage):
    def __init__(self, app, *args, **kwargs):
        """ Page 1 config

        :param app: Tkinter (GUI builder) setup
        :type app: class
        :param args: Tkinter's arguments
        :type args: Optional
        :param kwargs: Tkinter's kwargs arguments
        :type kwargs: Optional
        """
        size = (app.cam_width, app.cam_height, 0, 0)
        DrawingPage.__init__(self, app, size, "p1", *args, **kwargs)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tki.Button(self.buttonframe, text="Snapshot", font=("Courier", 44), width=9,
                                       command=self.snapshot_origin)
        self.btn_snapshot.place(relx=0.38, rely=0.05)
        self.btn_save.place(relx=0.56, rely=0.05)
        # self.btn_save = tki.Button(self.buttonframe, text="Save", font=("Courier", 44), width=9, command=self.save_draw)
        # self.btn_save.place(relx=0.56, rely=0.05)
        self.browsebutton = tki.Button(self.buttonframe, text="Browse", font=("Courier", 44), width=9, command=self.browse)
        self.browsebutton.place(relx=0.74, rely=0.05)
        self.btn_compare = tki.Button(self.buttonframe, text="Compare", font=("Courier", 44), width=9,
                                      command=self.snapshot_compare)
        self.btn_compare.place(relx=0.38, rely=0.18)
        self.btn_reset = tki.Button(self.buttonframe, text="Reset", font=("Courier", 44), width=9, command=self.reset)
        self.btn_reset.place(relx=0.56, rely=0.18)
        self.btn_mode_detect.place(relx=0.74, rely=0.18)
        self.btn_mode_inside.place(relx=0.81, rely=0.18)
        self.btn_mode_area.place(relx=0.88, rely=0.18)

        # todo remove or use ?
        self.pathlabel = tki.Label(self.buttonframe)
        self.pathlabel.place(relx=0.41, rely=0.25)

        # Result
        lbl_result = tki.Label(self.buttonframe, text="Result", font=("Courier", 44))
        lbl_result.place(relx=0.83, rely=0.35)
        self.lbl_result = tki.Label(self.buttonframe, text="        ", bg="yellow", font=("Courier", 44))
        self.lbl_result.place(relx=0.83, rely=0.44)

        # Drawing cv
        self.canvas2.place(relx=0.05, rely=0.35)
        self.canvas2.config(width=app.cam_width, height=app.cam_height)

        # Check latest data
        list_of_files = glob.glob('data/*')  # * means all if need specific format then *.csv
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            self.read_raw_data(latest_file)

        self.canvas3 = tki.Canvas(self.buttonframe)
        self.canvas3.place(relx=0.45, rely=0.35)
        self.canvas3.config(width=app.cam_width, height=app.cam_height)

    def reset(self):
        """Reset screen and parameters"""
        if self.save_status:
            self.save_status = False
            self.toggle_save_status()

        self.canvas2.delete("all")
        self.canvas3.delete("all")
        self.app.range_rgb = copy.deepcopy(init_param["drawing"]["range_rgb"])
        self.app.undo_rgb(None)

        self.file_path_o = ""
        self.load_img_o = ""
        self.tk_photo_org = ""
        self.pathlabel.config(text="")
        self.lbl_result.config(text="        ", bg="yellow")
        for mode in self.drawing_data:
            for draw_line in self.drawing_data[mode]["prev"]:
                self.canvas2.delete(draw_line)
        self.raw_data_draw = copy.deepcopy(init_param["load_data"]["raw_data_draw"])
        self.drawing_data = copy.deepcopy(init_param["drawing"]["drawing_data"])
        self.count_draw_sub_pol = 0
        self.start_x, self.start_y = 0, 0

    def snapshot(self, mode):
        """ Get a frame from the video source """
        if mode == "original" and self.tk_photo_org:
            msg_type = "Error"
            msg = "Need <reset> before <snapshot>"
            messagebox.showerror(msg_type, msg)
            raise Exception(msg_type + ": " + msg)

        cur_date = datetime.date.today()
        sub_dir = "%s/%s/%s/" % (str(cur_date.year), str(cur_date.month), str(cur_date.day))

        start_task = time.time()
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        if mode == "original":
            ret, frame, contours, mask = self.vid.get_frame(self.config, self.raw_data_draw)
            if ret:
                init_dir(self.app.out_path, sub_dir)
                self.file_path_o = self.app.out_path + sub_dir + "o_" + filename
                cv2.imwrite(self.file_path_o, cv2.cvtColor(mask, cv2.COLOR_RGB2BGR))
                self.load_img_o = Image.open(self.file_path_o)
                self.load_img_o = self.load_img_o.resize((self.size[0], self.size[1]), Image.ANTIALIAS)
                self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(self.size[2], self.size[3], image=self.tk_photo_org, anchor=tki.NW)

        elif mode == "compare":
            if self.save_status:
                ret, frame, contours, mask = self.vid.get_frame(self.config, self.raw_data_draw, auto_calibrate=True, reset=self.reset_calibrate)
                self.reset_calibrate = False
                if ret:
                    start = time.time()
                    init_dir(self.app.cp_path, sub_dir)
                    self.file_path_c = self.app.cp_path + sub_dir + "c_" + "temp_filename.jpg"
                    origin_image = self.vid.get_original_frame()
                    cv2.imwrite(self.file_path_c, cv2.cvtColor(origin_image, cv2.COLOR_RGB2BGR))
                    self.load_img_cp = Image.open(self.file_path_c)

                    self.load_img_cp = self.load_img_cp.resize((self.size[0], self.size[1]), Image.ANTIALIAS)

                    error_over, error_under = self.get_result(contours)
                    end = time.time()
                    print("Calculate time: %f" % (end - start))
                    self.tk_photo_cp = ImageTk.PhotoImage(image=self.load_img_cp)
                    self.canvas3.delete("all")
                    self.canvas3.create_image(self.size[2], self.size[3], image=self.tk_photo_cp, anchor=tki.NW)
                    output_status = "        "
                    if error_under:
                        output_status = "NG:UNDER"
                        for key in self.error_line:
                            self.canvas3.delete(self.error_line[key])
                        for i, lack_line in enumerate(error_under):
                            if len(lack_line) > 2:
                                self.error_box[i] = self.canvas3.create_line(lack_line, fill='blue', width=2)
                                self.canvas3.create_text((lack_line[2] + 10, lack_line[3]), text=i + 1,
                                                         font=('Impact', -15),
                                                         fill="blue")

                    if error_over:
                        if output_status == "NG:UNDER":
                            output_status = "NG:BOTH"
                        else:
                            output_status = "NG:OVER"
                        for i, over_line in enumerate(error_over):
                            self.error_box[i] = self.canvas3.create_line(
                                over_line[0][0], over_line[0][1], over_line[1][0], over_line[1][1],
                                fill='red', width=2)
                            self.canvas3.create_text((over_line[1][0] + 10, over_line[1][1]), text=i + 1,
                                                     font=('Impact', -15), fill="red")

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
                    # todo log.info(msg)
                    self.app.log.info(msg)

                    # use PIL to convert  PS to PNG
                    self.canvas3.update()
                    if output_status == "OK":
                        filename = self.app.cp_path + sub_dir + file_time_form + "_" + "OK"
                    else:
                        filename = self.app.cp_path + sub_dir + file_time_form + "_" + "NG"
                    filename_png = filename + ".png"
                    ps = self.canvas3.postscript(colormode='color')
                    img = Image.open(io.BytesIO(ps.encode('utf-8')))
                    img.save(filename_png)

                    end_task = time.time()
                    print("Calculate event time: %f" % (end_task - start_task))
                else:
                    msg_type = "Error"
                    msg = "Need <save> before <compare>"
                    messagebox.showerror(msg_type, msg)
                    raise Exception(msg_type + ": " + msg)

    def snapshot_origin(self):
        """ Call snapshot function with original image(LEFT)"""
        self.snapshot("original")

    def snapshot_compare(self):
        """ Call snapshot function with compare image(RIGHT)"""
        self.snapshot("compare")

    def get_result(self, contours):
        """Load rectangle and filename data from json file and return result"""
        if self.load_filename:
            with open(self.load_filename, 'r') as fp:
                self.raw_data_draw = json.load(fp)
                self.load_filename = None
        else:
            try:
                with open('data/data_%s.json' % self.file_path_o[:-4].split("/")[-1], 'r') as fp:
                    self.raw_data_draw = json.load(fp)
            except Exception:
                msg_type = "Error"
                msg = "Click <Save button> before <compare>"
                messagebox.showerror(msg_type, msg)
                raise Exception(msg_type + ": " + msg)
        error_cnt, error_lack = et.detect_error_cnt(contours, self.raw_data_draw, self.config)
        if self.app.TEST_MAMOS:
            if error_cnt or error_lack:
                self.app.mm.control(self.app.LED_NG)
            else:
                self.app.mm.control(self.app.LED_OK)
        return error_cnt, error_lack

    def browse(self):
        """Find json data from Local PC"""
        self.load_filename = filedialog.askopenfilename()
        self.pathlabel.config(text=self.load_filename)
        self.reset()
        self.read_raw_data(self.load_filename)
