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


class DrawingControl:
    def __init__(self, app, window, canvas2, buttonframe):
        self.window = window
        self.app = app
        self.canvas2 = canvas2

        self.buttonframe = buttonframe

        # Load data
        self.raw_data_draw = copy.deepcopy(init_param["load_data"]["raw_data_draw"])

        # Drawing
        self.drawing_data = copy.deepcopy(init_param["drawing"]["drawing_data"])
        self.prev_sub_pol = []
        self.count_draw_sub_pol = 0
        self.start_x, self.start_y = 0, 0

        # Status
        self.mode = "detect"

        #
        self.canvas2.bind("<ButtonPress-1>", self.on_button_press)
        # self.canvas2.bind("<B1-Motion>", self.on_move_press)
        # self.canvas2.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas2.bind("<Button-3>", self.undo)

        self.btn_mode_detect = tki.Button(self.buttonframe, text="DO", font=("Courier", 44),
                                          command=self.mode_detect, bg=self.drawing_data["detect"]["color"])
        self.btn_mode_detect.place(relx=0.74, rely=0.18)
        self.btn_mode_inside = tki.Button(self.buttonframe, text="DI", font=("Courier", 44), command=self.mode_inside)
        self.btn_mode_inside.place(relx=0.81, rely=0.18)
        self.btn_mode_area = tki.Button(self.buttonframe, text="Area", font=("Courier", 44), command=self.mode_area)
        self.btn_mode_area.place(relx=0.88, rely=0.18)

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
        """ Draw mode: inside """
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
        if self.app.p1.save_status:
            self.app.p1.toggle_save_status()

        if self.app.p1.load_img_o:
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

                        flat_polygon = [item for sublist in self.drawing_data[self.mode]["temp_pol"] for item in sublist]
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
        if self.app.p1.save_status:
            self.app.p1.toggle_save_status()

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
