from typing import Dict, List, Any

import tkinter as tki
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

from src import extraction as et
from gui.page_control import Page
# from gui.drawing_control import DrawingControl
import init_project
from init_project import init_dir

# Load init params
init_param = init_project.init_param()


class Page1(Page):
    raw_data_draw = ...  # type: Dict["filename":str, "detect":List[str, List[Any]], "inside":List[str, List[Any]], "area":List[str, List[Any]]]
    drawing_data = ...  # type: Dict[str, Dict["color": str, "prev": Dict, "polygon": Dict]]

    def __init__(self, app, *args, **kwargs):
        """ Page 1 config

        :param app: Tkinter (GUI builder) setup
        :type app: class
        :param args: Tkinter's arguments
        :type args: Optional
        :param kwargs: Tkinter's kwargs arguments
        :type kwargs: Optional
        """
        self.vid = app.vid
        self.config = app.config
        self.window = self
        self.app = app

        Page.__init__(self, app, *args, **kwargs)

        # Button that lets the user take a snapshot
        self.btn_snapshot.place(relx=0.38, rely=0.05)

        self.btn_save.place(relx=0.56, rely=0.05)

        self.browsebutton.place(relx=0.74, rely=0.05)

        self.btn_compare.place(relx=0.38, rely=0.18)

        self.btn_reset.place(relx=0.56, rely=0.18)

        self.btn_mode_detect.place(relx=0.74, rely=0.18)
        self.btn_mode_inside.place(relx=0.81, rely=0.18)
        self.btn_mode_area.place(relx=0.88, rely=0.18)

        # todo remove or use ?
        self.pathlabel.place(relx=0.41, rely=0.25)

        # Result
        self.lbl_result.place(relx=0.83, rely=0.44)

        # Drawing cv
        self.canvas2.place(relx=0.05, rely=0.35)
        self.canvas2.bind("<ButtonPress-1>", self.on_button_press)
        # self.canvas2.bind("<B1-Motion>", self.on_move_press)
        # self.canvas2.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas2.bind("<Button-3>", self.undo)
        self.canvas2.config(width=app.cam_width, height=app.cam_height)

        # Check latest data
        list_of_files = glob.glob('data/*')  # * means all if need specific format then *.csv
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            self.read_raw_data(latest_file)

        self.canvas3.place(relx=0.45, rely=0.35)
        self.canvas3.config(width=app.cam_width, height=app.cam_height)

        # DrawingControl(self)

    # def reset(self):
    #     """Reset screen and parameters"""
    #     self.toggle_save_status()
    #     self.canvas2.delete("all")
    #     self.canvas3.delete("all")
    #     self.app.range_rgb = copy.deepcopy(init_param["drawing"]["range_rgb"])
    #     self.app.undo_rgb(None)
    #
    #     self.file_path_o = ""
    #     self.load_img_o = ""
    #     self.tk_photo_org = ""
    #     self.pathlabel.config(text="")
    #     self.lbl_result.config(text="        ", bg="yellow")
    #     for mode in self.drawing_data:
    #         for draw_line in self.drawing_data[mode]["prev"]:
    #             self.canvas2.delete(draw_line)
    #     self.raw_data_draw = copy.deepcopy(init_param["load_data"]["raw_data_draw"])
    #     self.drawing_data = copy.deepcopy(init_param["drawing"]["drawing_data"])
    #     self.count_draw_sub_pol = 0
    #     self.start_x, self.start_y = 0, 0
    #
    # def mode_default(self):
    #     """ Change draw mode buttons to default """
    #     self.btn_mode_detect = tki.Button(self.window, text="DO", font=("Courier", 44), command=self.mode_detect)
    #     self.btn_mode_detect.place(relx=0.74, rely=0.18)
    #     self.btn_mode_inside = tki.Button(self.window, text="DI", font=("Courier", 44), command=self.mode_inside)
    #     self.btn_mode_inside.place(relx=0.81, rely=0.18)
    #     self.btn_mode_area = tki.Button(self.window, text="Area", font=("Courier", 44), command=self.mode_area)
    #     self.btn_mode_area.place(relx=0.88, rely=0.18)
    #
    #     # Remove drawing
    #     for draw_line in self.prev_sub_pol:
    #         self.canvas2.delete(draw_line)
    #     self.drawing_data[self.mode]["temp_pol"] = []
    #     self.prev_sub_pol = []
    #     self.count_draw_sub_pol = 0
    #     self.start_x, self.start_y = 0, 0
    #
    # def mode_detect(self):
    #     """ Draw mode: detect """
    #     self.mode_default()
    #     self.btn_mode_detect = tki.Button(self.window, text="DO", font=("Courier", 44),
    #                                       command=self.mode_detect, bg=self.drawing_data["detect"]["color"])
    #     self.btn_mode_detect.place(relx=0.74, rely=0.18)
    #     self.mode = "detect"
    #
    # def mode_inside(self):
    #     self.mode_default()
    #     self.btn_mode_inside = tki.Button(self.window, text="DI", font=("Courier", 44),
    #                                       command=self.mode_inside, bg=self.drawing_data["inside"]["color"])
    #     self.btn_mode_inside.place(relx=0.81, rely=0.18)
    #     self.mode = "inside"
    #
    # def mode_area(self):
    #     """ Draw mode: area """
    #     self.mode_default()
    #     self.btn_mode_area = tki.Button(self.window, text="Area", font=("Courier", 44), command=self.mode_area,
    #                                     bg=self.drawing_data["area"]["color"])
    #     self.btn_mode_area.place(relx=0.88, rely=0.18)
    #     self.mode = "area"
    #
    # def on_button_press(self, event):
    #     """ Left Click events in canvas"""
    #     if self.save_status:
    #         self.toggle_save_status()
    #
    #     if self.load_img_o:
    #         x, y = event.x, event.y
    #         if self.start_x and self.start_y:
    #             if self.mode == "inside":
    #                 self.drawing_data[self.mode]["prev"].append(
    #                     self.canvas2.create_line(
    #                         x, y, self.start_x, self.start_y, width=2, fill=self.drawing_data[self.mode]["color"]))
    #                 if self.start_x < x:
    #                     blue_line = [self.start_x, self.start_y, x, y]
    #                 else:
    #                     blue_line = [x, y, self.start_x, self.start_y]
    #                 self.raw_data_draw[self.mode].append(blue_line)
    #                 self.start_x, self.start_y = 0, 0
    #             else:
    #                 if abs(x - self.start_x) < 20 and abs(y - self.start_y) < 20:
    #                     for draw_line in self.prev_sub_pol:
    #                         self.canvas2.delete(draw_line)
    #                     self.prev_sub_pol = []
    #                     self.count_draw_sub_pol = 0
    #
    #                     flat_polygon = [item for sublist in self.drawing_data[self.mode]["temp_pol"] for item in sublist]
    #                     if self.mode == "area":
    #                         # todo area more than 1
    #                         if self.drawing_data[self.mode]["prev"]:
    #                             self.canvas2.delete(self.drawing_data[self.mode]["prev"])
    #                             self.drawing_data[self.mode]["prev"] = []
    #                             self.drawing_data[self.mode]["polygon"] = []
    #                     self.drawing_data[self.mode]["prev"].append([self.canvas2.create_polygon(
    #                         flat_polygon, outline=self.drawing_data[self.mode]["color"], fill="", width=2)])
    #                     self.drawing_data[self.mode]["polygon"].append(self.drawing_data[self.mode]["temp_pol"])
    #                     self.raw_data_draw[self.mode] = self.drawing_data[self.mode]["polygon"]
    #                     self.drawing_data[self.mode]["temp_pol"] = []
    #                     self.start_x, self.start_y = 0, 0
    #                 else:
    #                     self.prev_sub_pol.append(
    #                         self.canvas2.create_line(x, y, self.drawing_data[self.mode]["temp_pol"][-1][0],
    #                                                  self.drawing_data[self.mode]["temp_pol"][-1][1], width=2,
    #                                                  fill=self.drawing_data[self.mode]["color"]))
    #                     self.count_draw_sub_pol += 1
    #                     self.drawing_data[self.mode]["temp_pol"].append([x, y])
    #         else:
    #             self.start_x, self.start_y = x, y
    #             self.drawing_data[self.mode]["temp_pol"].append([x, y])
    #
    # def undo(self, event):
    #     """ Right click events in canvas"""
    #     if self.save_status:
    #         self.toggle_save_status()
    #
    #     if self.mode == "inside":
    #         if self.drawing_data[self.mode]["prev"]:
    #             self.canvas2.delete(self.drawing_data[self.mode]["prev"][-1])
    #             del self.drawing_data[self.mode]["prev"][-1]
    #             del self.drawing_data[self.mode]["polygon"][-1]
    #             self.raw_data_draw[self.mode] = self.drawing_data[self.mode]["polygon"]
    #     else:
    #         if self.count_draw_sub_pol:
    #             # remove sub-polygon
    #             self.canvas2.delete(self.prev_sub_pol[-1])
    #             del self.prev_sub_pol[-1]
    #             del self.drawing_data[self.mode]["temp_pol"][-1]
    #             self.count_draw_sub_pol -= 1
    #             if not self.count_draw_sub_pol:
    #                 self.start_x, self.start_y = 0, 0
    #                 del self.drawing_data[self.mode]["temp_pol"][-1]
    #         else:
    #             # remove last polygon
    #             if self.drawing_data[self.mode]["polygon"]:
    #                 del self.drawing_data[self.mode]["polygon"][-1]
    #                 self.raw_data_draw[self.mode] = self.drawing_data[self.mode]["polygon"]
    #                 self.canvas2.delete(self.drawing_data[self.mode]["prev"][-1])
    #                 del self.drawing_data[self.mode]["prev"][-1]
    #
    # def snapshot(self, mode):
    #     """ Get a frame from the video source """
    #     if mode == "original" and self.tk_photo_org:
    #         msg_type = "Error"
    #         msg = "Need <reset> before <snapshot>"
    #         messagebox.showerror(msg_type, msg)
    #         raise Exception(msg_type + ": " + msg)
    #
    #     cur_date = datetime.date.today()
    #     sub_dir = "%s/%s/%s/" % (str(cur_date.year), str(cur_date.month), str(cur_date.day))
    #
    #     start_task = time.time()
    #     ret, frame, contours, mask = self.vid.get_frame(self.config, self.raw_data_draw, self.save_status)
    #
    #     end = time.time()
    #     print("Capture time: %f" % (end - start_task))
    #     ts = datetime.datetime.now()
    #     filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
    #
    #     if ret:
    #         if mode == "original":
    #             init_dir(self.app.out_path, sub_dir)
    #             self.file_path_o = self.app.out_path + sub_dir + "o_" + filename
    #             cv2.imwrite(self.file_path_o, cv2.cvtColor(mask, cv2.COLOR_RGB2BGR))
    #             self.load_img_o = Image.open(self.file_path_o)
    #             size = [self.app.cam_width, self.app.cam_height, 0, 0]
    #             self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
    #             self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
    #             self.canvas2.create_image(size[2], size[3], image=self.tk_photo_org, anchor=tki.NW)
    #
    #         elif mode == "compare":
    #             if self.save_status:
    #                 start = time.time()
    #                 init_dir(self.app.cp_path, sub_dir)
    #                 self.file_path_c = self.app.cp_path + sub_dir + "c_" + "temp_filename.jpg"
    #                 cv2.imwrite(self.file_path_c, cv2.cvtColor(self.app.frame, cv2.COLOR_RGB2BGR))
    #                 self.load_img_cp = Image.open(self.file_path_c)
    #
    #                 size = [self.app.cam_width, self.app.cam_height, 0, 0]
    #                 self.load_img_cp = self.load_img_cp.resize((size[0], size[1]), Image.ANTIALIAS)
    #
    #                 error_over, error_under = self.get_result(contours)
    #                 end = time.time()
    #                 print("Calculate time: %f" % (end - start))
    #                 self.tk_photo_cp = ImageTk.PhotoImage(image=self.load_img_cp)
    #                 self.canvas3.delete("all")
    #                 self.canvas3.create_image(size[2], size[3], image=self.tk_photo_cp, anchor=tki.NW)
    #                 output_status = "        "
    #                 if error_under:
    #                     output_status = "NG:UNDER"
    #                     for key in self.error_line:
    #                         self.canvas3.delete(self.error_line[key])
    #                     for i, lack_line in enumerate(error_under):
    #                         if len(lack_line) > 2:
    #                             self.error_box[i] = self.canvas3.create_line(lack_line, fill='blue', width=2)
    #                             self.canvas3.create_text((lack_line[2] + 10, lack_line[3]), text=i + 1,
    #                                                      font=('Impact', -15),
    #                                                      fill="blue")
    #
    #                 if error_over:
    #                     if output_status == "NG:UNDER":
    #                         output_status = "NG:BOTH"
    #                     else:
    #                         output_status = "NG:OVER"
    #                     for i, over_line in enumerate(error_over):
    #                         self.error_box[i] = self.canvas3.create_line(
    #                             over_line[0][0], over_line[0][1], over_line[1][0], over_line[1][1],
    #                             fill='red', width=2)
    #                         self.canvas3.create_text((over_line[1][0] + 10, over_line[1][1]), text=i + 1,
    #                                                  font=('Impact', -15), fill="red")
    #
    #                 if not error_under and not error_over:
    #                     output_status = "OK"
    #
    #                 # Output Screen
    #                 if output_status == "OK":
    #                     self.lbl_result.config(text=output_status, bg="green")
    #                 else:
    #                     self.lbl_result.config(text=output_status, bg="red")
    #
    #                 # Output log
    #                 cur_time = datetime.datetime.now()
    #                 file_time_form = cur_time.strftime("%Y%m%d_%H%M%S")
    #                 log_time_form = cur_time.strftime("%Y:%m:%d %H:%M:%S")
    #                 msg = log_time_form + "> Output: " + output_status + " | Over count: %d | Under count:  %d" % (
    #                     len(error_over), len(error_under))
    #                 # todo log.info(msg)
    #                 self.app.log.info(msg)
    #
    #                 # use PIL to convert  PS to PNG
    #                 self.canvas3.update()
    #                 if output_status == "OK":
    #                     filename = self.app.cp_path + sub_dir + file_time_form + "_" + "OK"
    #                 else:
    #                     filename = self.app.cp_path + sub_dir + file_time_form + "_" + "NG"
    #                 filename_png = filename + ".png"
    #                 ps = self.canvas3.postscript(colormode='color')
    #                 img = Image.open(io.BytesIO(ps.encode('utf-8')))
    #                 img.save(filename_png)
    #
    #                 end_task = time.time()
    #                 print("Calculate event time: %f" % (end_task - start_task))
    #             else:
    #                 msg_type = "Error"
    #                 msg = "Need <save> before <compare>"
    #                 messagebox.showerror(msg_type, msg)
    #                 raise Exception(msg_type + ": " + msg)
    #
    # def load_draw(self):
    #     for mode in self.drawing_data:
    #         if self.raw_data_draw[mode]:
    #             if mode == "inside":
    #                 lines = self.raw_data_draw["inside"]
    #                 if lines:
    #                     for line in lines:
    #                         self.drawing_data[mode]["prev"].append(
    #                             self.canvas2.create_line(line[0], line[1], line[2], line[3], width=2, fill='blue'))
    #             else:
    #                 for polygon in self.raw_data_draw[mode]:
    #                     flat_polygon = [item for sublist in polygon for item in sublist]
    #                     self.drawing_data[mode]["prev"].append(self.canvas2.create_polygon(
    #                         flat_polygon, outline=self.drawing_data[mode]["color"], fill="", width=2))
    #             self.drawing_data[mode]["polygon"] = self.raw_data_draw[mode]
    #
    # def snapshot_origin(self):
    #     """ Call snapshot function with original image(LEFT)"""
    #     self.snapshot("original")
    #
    # def snapshot_compare(self):
    #     """ Call snapshot function with compare image(RIGHT)"""
    #     self.snapshot("compare")
    #
    # def save_draw(self):
    #     """ Save drawing data to json file"""
    #     if (not self.raw_data_draw["detect"]) or (not self.raw_data_draw["area"]):
    #         msg_type = "Error"
    #         msg = "Need <draw> and <area> before <save>"
    #         messagebox.showerror(msg_type, msg)
    #         raise Exception(msg_type + ": " + msg)
    #
    #     # Save setting data
    #     self.raw_data_draw["filename"] = self.file_path_o
    #     data = json.dumps(self.raw_data_draw)
    #     filename = 'data/data_%s.json' % self.file_path_o[:-4].split("/")[-1]
    #     with open(filename, 'w') as fp:
    #         fp.write(data)
    #     print("SAVE !", 'data/data_%s.json' % self.file_path_o[:-4].split("/")[-1])
    #     # self.raw_data_draw = init_param["load_data"]["raw_data_draw"]
    #     self.reset()
    #     self.read_raw_data(filename)
    #
    #     # Save setting image
    #     self.canvas2.update()
    #     filename_png = self.file_path_o.replace("/o_", "/s_")
    #     ps = self.canvas2.postscript(colormode='color')
    #     img = Image.open(io.BytesIO(ps.encode('utf-8')))
    #     img.save(filename_png)
    #
    # def get_result(self, contours):
    #     """Load rectangle and filename data from json file and return result"""
    #     if self.load_filename:
    #         with open(self.load_filename, 'r') as fp:
    #             self.raw_data_draw = json.load(fp)
    #             self.load_filename = None
    #     else:
    #         try:
    #             with open('data/data_%s.json' % self.file_path_o[:-4].split("/")[-1], 'r') as fp:
    #                 self.raw_data_draw = json.load(fp)
    #         except Exception:
    #             msg_type = "Error"
    #             msg = "Click <Save button> before <compare>"
    #             messagebox.showerror(msg_type, msg)
    #             raise Exception(msg_type + ": " + msg)
    #     error_cnt, error_lack = et.detect_error_cnt(contours, self.raw_data_draw, self.config)
    #     if self.app.TEST_MAMOS:
    #         if error_cnt or error_lack:
    #             self.app.mm.control(self.app.LED_NG)
    #         else:
    #             self.app.mm.control(self.app.LED_OK)
    #     return error_cnt, error_lack
    #
    # def read_raw_data(self, filename):
    #     """Read json data and update canvas"""
    #     if filename:
    #         with open(filename, 'r') as fp:
    #             self.toggle_save_status(True)
    #
    #             self.raw_data_draw = json.load(fp)
    #
    #             # load img
    #             print("Loading data: ")
    #             print(self.raw_data_draw)
    #             self.load_img_o = Image.open(self.raw_data_draw["filename"])
    #             self.file_path_o = self.raw_data_draw["filename"]
    #             size = [self.app.cam_width, self.app.cam_height, 0, 0]
    #             self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
    #             self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
    #             self.canvas2.create_image(size[2], size[3], image=self.tk_photo_org, anchor=tki.NW)
    #
    #             # load draw
    #             self.load_draw()
    #
    # def browse(self):
    #     """Find json data from Local PC"""
    #     self.load_filename = filedialog.askopenfilename()
    #     self.pathlabel.config(text=self.load_filename)
    #     self.reset()
    #     self.read_raw_data(self.load_filename)
    #
    # def toggle_save_status(self, status=False):
    #     """Toggle snapshot status"""
    #     self.save_status = status
    #     if status:
    #         self.btn_save = tki.Button(self.window, text="Save", bg='green', font=("Courier", 44), width=9,
    #                                    command=self.save_draw)
    #     else:
    #         self.btn_save = tki.Button(self.window, text="Save", font=("Courier", 44), width=9, command=self.save_draw)
    #     self.btn_save.place(relx=0.56, rely=0.05)
