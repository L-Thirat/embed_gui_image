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
import init_project
from init_project import init_dir
# Load init params
init_param = init_project.init_param()


class DrawingPage(tki.Frame):
    raw_data_draw = ...  # type: Dict["filename":str, "detect":List[str, List[Any]], "inside":List[str, List[Any]], "area":List[str, List[Any]]]
    drawing_data = ...  # type: Dict[str, Dict["color": str, "prev": Dict, "polygon": Dict]]

    def __init__(self, app, size, page, *args, **kwargs):
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
        self.size = size
        self.page = page

        tki.Frame.__init__(self, *args, **kwargs)

        # Load data
        self.file_path_o = ""
        self.file_path_c = ""
        self.tk_photo_line = None
        self.tk_photo_org = None
        self.tk_photo_cp = None
        self.load_img_o = None
        self.load_img_cp = None
        self.load_filename = None
        self.raw_data_draw = copy.deepcopy(init_param["load_data"]["raw_data_draw"])

        # Output display
        self.error_box = {}
        self.error_line = {}

        # Drawing
        self.drawing_data = copy.deepcopy(init_param["drawing"]["drawing_data"])
        self.prev_sub_pol = []
        self.count_draw_sub_pol = 0
        self.start_x, self.start_y = 0, 0

        # Status
        self.save_status = False
        self.mode = "detect"

        buttonframe = tki.Frame(self)
        buttonframe.pack(side="top", fill="both", expand=True)
        self.buttonframe = buttonframe

        # Button that lets the user take a snapshot
        # self.btn_snapshot = tki.Button(buttonframe, text="Snapshot", font=("Courier", 44), width=9,
        #                                command=self.snapshot_origin)
        # self.btn_snapshot.place(relx=0.38, rely=0.05)

        self.btn_save = tki.Button(buttonframe, text="Save", font=("Courier", 44), width=9, command=self.save_draw)

        # self.browsebutton = tki.Button(buttonframe, text="Browse", font=("Courier", 44), width=9, command=self.browse)
        # self.browsebutton.place(relx=0.74, rely=0.05)

        # self.btn_compare = tki.Button(buttonframe, text="Compare", font=("Courier", 44), width=9,
        #                               command=self.snapshot_compare)
        # self.btn_compare.place(relx=0.38, rely=0.18)

        # self.btn_reset = tki.Button(buttonframe, text="Reset", font=("Courier", 44), width=9, command=self.reset)
        # self.btn_reset.place(relx=0.56, rely=0.18)

        self.btn_mode_detect = tki.Button(buttonframe, text="DO", font=("Courier", 44),
                                          command=self.mode_detect, bg=self.drawing_data["detect"]["color"])
        # self.btn_mode_detect.place(relx=0.74, rely=0.18)
        self.btn_mode_inside = tki.Button(buttonframe, text="DI", font=("Courier", 44), command=self.mode_inside)
        # self.btn_mode_inside.place(relx=0.81, rely=0.18)
        self.btn_mode_area = tki.Button(buttonframe, text="Area", font=("Courier", 44), command=self.mode_area)
        # self.btn_mode_area.place(relx=0.88, rely=0.18)

        # self.pathlabel = tki.Label(buttonframe)
        # self.pathlabel.place(relx=0.41, rely=0.25)

        # Result
        # lbl_result = tki.Label(buttonframe, text="Result", font=("Courier", 44))
        # lbl_result.place(relx=0.83, rely=0.35)
        # self.lbl_result = tki.Label(buttonframe, text="        ", bg="yellow", font=("Courier", 44))
        # self.lbl_result.place(relx=0.83, rely=0.44)

        # Drawing cv
        self.canvas2 = tki.Canvas(buttonframe, cursor="cross")
        # self.canvas2.place(relx=0.05, rely=0.35)
        self.canvas2.bind("<ButtonPress-1>", self.on_button_press)
        # self.canvas2.bind("<B1-Motion>", self.on_move_press)
        # self.canvas2.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas2.bind("<Button-3>", self.undo)
        # self.canvas2.config(width=app.cam_width, height=app.cam_height)

        # # Check latest data
        # list_of_files = glob.glob('data/*')  # * means all if need specific format then *.csv
        # if list_of_files:
        #     latest_file = max(list_of_files, key=os.path.getctime)
        #     self.read_raw_data(latest_file)
        #
        # self.canvas3 = tki.Canvas(buttonframe)
        # # self.canvas3.place(relx=0.45, rely=0.35)
        # self.canvas3.config(width=app.cam_width, height=app.cam_height)

    def drawing_scale(self, zoom):
        # if zoom > 1:
        for mode in self.drawing_data:
            self.drawing_data[mode]["prev"] = []
            if mode == "inside":
                scaled = [[int(p * zoom) for p in l] for l in self.drawing_data[mode]["polygon"]]
                self.drawing_data[mode]["polygon"] = scaled
                self.raw_data_draw[mode] = scaled
            else:
                for i, pol in enumerate(self.drawing_data[mode]["polygon"]):
                    for j, p in enumerate(pol):
                        scaled = [int(p[0] * zoom), int(p[1] * zoom)]
                        self.drawing_data[mode]["polygon"][i][j] = scaled
                        self.raw_data_draw[mode][i][j] = scaled

    def show(self, p1=None, p3=None):
        if p1:
            # To page 3
            self.save_status = True
            self.file_path_o = p1.file_path_o
            self.load_img_o = Image.open(self.file_path_o)
            self.load_img_o = self.load_img_o.resize((self.size[0], self.size[1]), Image.ANTIALIAS)
            self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
            self.canvas2.create_image(self.size[2], self.size[3], image=self.tk_photo_org, anchor=tki.NW)
            self.canvas2.place(relx=0.05, rely=0.1)

            self.drawing_data = p1.drawing_data
            self.raw_data_draw = p1.raw_data_draw
            self.drawing_scale(1.5)
            self.load_draw()
        elif p3:
            # To page 1
            self.save_status = True
            self.toggle_save_status(self.save_status)
            # self.file_path_o = p3.file_path_o

            self.drawing_data = p3.drawing_data
            self.raw_data_draw = p3.raw_data_draw
            self.drawing_scale(2/3)
            self.save_draw()

            filename = 'data/data_%s.json' % p3.file_path_o[:-4].split("/")[-1]
            self.reset()
            self.read_raw_data(filename)
        self.lift()

    def mode_default(self):
        """ Change draw mode buttons to default """
        self.btn_mode_detect = tki.Button(self.window, text="DO", font=("Courier", 44), command=self.mode_detect)
        self.btn_mode_detect.place(relx=0.74, rely=0.18)
        self.btn_mode_inside = tki.Button(self.window, text="DI", font=("Courier", 44), command=self.mode_inside)
        self.btn_mode_inside.place(relx=0.81, rely=0.18)
        self.btn_mode_area = tki.Button(self.window, text="Area", font=("Courier", 44), command=self.mode_area)
        self.btn_mode_area.place(relx=0.88, rely=0.18)

        # Remove drawing
        for draw_line in self.prev_sub_pol:
            self.canvas2.delete(draw_line)
        self.drawing_data[self.mode]["temp_pol"] = []
        self.prev_sub_pol = []
        self.count_draw_sub_pol = 0
        self.start_x, self.start_y = 0, 0

    def mode_detect(self):
        """ Draw mode: detect """
        self.mode_default()
        self.btn_mode_detect = tki.Button(self.window, text="DO", font=("Courier", 44),
                                          command=self.mode_detect, bg=self.drawing_data["detect"]["color"])
        self.btn_mode_detect.place(relx=0.74, rely=0.18)
        self.mode = "detect"

    def mode_inside(self):
        self.mode_default()
        self.btn_mode_inside = tki.Button(self.window, text="DI", font=("Courier", 44),
                                          command=self.mode_inside, bg=self.drawing_data["inside"]["color"])
        self.btn_mode_inside.place(relx=0.81, rely=0.18)
        self.mode = "inside"

    def mode_area(self):
        """ Draw mode: area """
        self.mode_default()
        self.btn_mode_area = tki.Button(self.window, text="Area", font=("Courier", 44), command=self.mode_area,
                                        bg=self.drawing_data["area"]["color"])
        self.btn_mode_area.place(relx=0.88, rely=0.18)
        self.mode = "area"

    def on_button_press(self, event):
        """ Left Click events in canvas"""
        if self.save_status:
            self.toggle_save_status()

        if self.load_img_o:
            x, y = event.x, event.y
            if self.start_x and self.start_y:
                if self.mode == "inside":
                    self.drawing_data[self.mode]["prev"].append(
                        self.canvas2.create_line(
                            x, y, self.start_x, self.start_y, width=2, fill=self.drawing_data[self.mode]["color"]))
                    if self.start_x < x:
                        blue_line = [self.start_x, self.start_y, x, y]
                    else:
                        blue_line = [x, y, self.start_x, self.start_y]
                    self.raw_data_draw[self.mode].append(blue_line)
                    self.start_x, self.start_y = 0, 0
                else:
                    if abs(x - self.start_x) < 20 and abs(y - self.start_y) < 20:
                        for draw_line in self.prev_sub_pol:
                            self.canvas2.delete(draw_line)
                        self.prev_sub_pol = []
                        self.count_draw_sub_pol = 0

                        flat_polygon = [item for sublist in self.drawing_data[self.mode]["temp_pol"] for item in
                                        sublist]
                        if self.mode == "area":
                            # todo area more than 1
                            if self.drawing_data[self.mode]["prev"]:
                                self.canvas2.delete(self.drawing_data[self.mode]["prev"])
                                self.drawing_data[self.mode]["prev"] = []
                                self.drawing_data[self.mode]["polygon"] = []
                        self.drawing_data[self.mode]["prev"].append([self.canvas2.create_polygon(
                            flat_polygon, outline=self.drawing_data[self.mode]["color"], fill="", width=2)])
                        self.drawing_data[self.mode]["polygon"].append(self.drawing_data[self.mode]["temp_pol"])
                        self.raw_data_draw[self.mode] = self.drawing_data[self.mode]["polygon"]
                        self.drawing_data[self.mode]["temp_pol"] = []
                        self.start_x, self.start_y = 0, 0
                    else:
                        self.prev_sub_pol.append(
                            self.canvas2.create_line(x, y, self.drawing_data[self.mode]["temp_pol"][-1][0],
                                                     self.drawing_data[self.mode]["temp_pol"][-1][1], width=2,
                                                     fill=self.drawing_data[self.mode]["color"]))
                        self.count_draw_sub_pol += 1
                        self.drawing_data[self.mode]["temp_pol"].append([x, y])
            else:
                self.start_x, self.start_y = x, y
                self.drawing_data[self.mode]["temp_pol"].append([x, y])

    def undo(self, event):
        """ Right click events in canvas"""
        if self.save_status:
            self.toggle_save_status()

        if self.mode == "inside":
            if self.drawing_data[self.mode]["prev"]:
                self.canvas2.delete(self.drawing_data[self.mode]["prev"][-1])
                del self.drawing_data[self.mode]["prev"][-1]
                del self.drawing_data[self.mode]["polygon"][-1]
                self.raw_data_draw[self.mode] = self.drawing_data[self.mode]["polygon"]
        else:
            if self.count_draw_sub_pol:
                # remove sub-polygon
                self.canvas2.delete(self.prev_sub_pol[-1])
                del self.prev_sub_pol[-1]
                del self.drawing_data[self.mode]["temp_pol"][-1]
                self.count_draw_sub_pol -= 1
                if not self.count_draw_sub_pol:
                    self.start_x, self.start_y = 0, 0
                    del self.drawing_data[self.mode]["temp_pol"][-1]
            else:
                # remove last polygon
                if self.drawing_data[self.mode]["polygon"]:
                    del self.drawing_data[self.mode]["polygon"][-1]
                    self.raw_data_draw[self.mode] = self.drawing_data[self.mode]["polygon"]
                    self.canvas2.delete(self.drawing_data[self.mode]["prev"][-1])
                    del self.drawing_data[self.mode]["prev"][-1]

    def toggle_save_status(self, status=False):
        """Toggle snapshot status"""
        if self.page == "p1":
            self.save_status = status
            if status:
                self.btn_save = tki.Button(self.window, text="Save", bg='green', font=("Courier", 44), width=9,
                                           command=self.save_draw)
            else:
                self.btn_save = tki.Button(self.window, text="Save", font=("Courier", 44), width=9, command=self.save_draw)
            self.btn_save.place(relx=0.56, rely=0.05)

    def load_draw(self):
        for mode in self.drawing_data:
            if self.raw_data_draw[mode]:
                if mode == "inside":
                    lines = self.raw_data_draw["inside"]
                    if lines:
                        for line in lines:
                            self.drawing_data[mode]["prev"].append(
                                self.canvas2.create_line(line[0], line[1], line[2], line[3], width=2, fill='blue'))
                else:
                    for polygon in self.raw_data_draw[mode]:
                        flat_polygon = [item for sublist in polygon for item in sublist]
                        self.drawing_data[mode]["prev"].append(self.canvas2.create_polygon(
                            flat_polygon, outline=self.drawing_data[mode]["color"], fill="", width=2))
                self.drawing_data[mode]["polygon"] = self.raw_data_draw[mode]

    def read_raw_data(self, filename):
        """Read json data and update canvas"""
        if filename:
            with open(filename, 'r') as fp:
                self.toggle_save_status(True)

                self.raw_data_draw = json.load(fp)

                # load img
                print("Loading data: ")
                print(self.raw_data_draw)
                self.load_img_o = Image.open(self.raw_data_draw["filename"])
                self.file_path_o = self.raw_data_draw["filename"]
                self.load_img_o = self.load_img_o.resize((self.size[0], self.size[1]), Image.ANTIALIAS)
                self.tk_photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(self.size[2], self.size[3], image=self.tk_photo_org, anchor=tki.NW)

                # load draw
                self.load_draw()

    def reset(self):
        pass

    def save_draw(self):
        """ Save drawing data to json file"""
        if (not self.raw_data_draw["detect"]) or (not self.raw_data_draw["area"]):
            msg_type = "Error"
            msg = "Need <draw> and <area> before <save>"
            messagebox.showerror(msg_type, msg)
            raise Exception(msg_type + ": " + msg)

        self.raw_data_draw["filename"] = self.file_path_o
        data = json.dumps(self.raw_data_draw)
        filename = 'data/data_%s.json' % self.file_path_o[:-4].split("/")[-1]
        with open(filename, 'w') as fp:
            fp.write(data)
        print("SAVE !", 'data/data_%s.json' % self.file_path_o[:-4].split("/")[-1])
        # self.raw_data_draw = init_param["load_data"]["raw_data_draw"]
        self.reset()
        self.read_raw_data(filename)

        # Save setting image
        self.canvas2.update()
        filename_png = self.file_path_o.replace("/o_", "/s_")
        ps = self.canvas2.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img.save(filename_png)
