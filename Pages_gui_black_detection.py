#!/usr/bin/env python3

# todo clear image in "/output/o_.jpg"
# todo camera moved detection
# todo program slowed when a lot function update realtime ex hue -> Need RUN/STOP Button when start/STOP
# todo multiple camera
# todo show line realtime (capture: Origin image)

# todo fix create new log file each day
# todo auto light calibrate
# todo GUI bug
"""
# Reference

Interpolation:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
"""

import tkinter as tki
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import imutils
import atexit
import yaml
import numpy as np
import copy

import init_project
from tkinter import messagebox

init_project.create_folders()
init_param = init_project.init_param()

from src import extraction as et
from src.video_capture import MyVideoCapture as Vdo
from gui import Page1, Page2, Page3
from PIL import EpsImagePlugin
from time import time

# Global variable
half_color_dot = 3
delay = 15


class App(tki.Frame):
    """ This Application is use to detect line in image using image processing technique on CV2 that GUI based on tkinter

    :param setting_data: Project settings
    :type setting_data: dict
    :param log: Log settings
    :type log: class
    :param LED_OK: Output OK PIN
    :type LED_OK: int
    :param LED_NG: Output NG PIN
    :type LED_NG: int
    :param BTN_input: Input PIN
    :type BTN_input: int
    :param DEBUG: Debug mode
    :type DEBUG: bool [True: Run debug mode, False: Run production]
    :param TEST_MAMOS: Test on Mamos mode
    :type TEST_MAMOS: bool [True: Run on mamos, False: Run on PC]
    :param mm: Mamos class
    :type mm: class
    :param config: Video config
    :type config: dict
    :param range_rgb: RGB checker
    :type range_rgb: list
    :param window: Tkinter (GUI builder) setup
    :type window: class
    :param vid: Video capture class
    :type vid: class
    :param frame: Video Capture's frame
    :type frame: class
    :param mask: Video Capture's mask
    :type mask: class
    :param cur_page: Current page
    :type cur_page: int
    :param prev_page: Previous page
    :type prev_page: int
    :param p1: Page1
    :type p1: class
    :param p2: Page2
    :type p2: class
    :param p3: Page3
    :type p3: class
    :param canvas_rt: Canvas
    :type canvas_rt: bool [True: Run on mamos, False: Run on PC]
    """
    def __init__(self, window, *args, **kwargs):
        """Constructor method"""
        # Setting
        with open(r'setting.yaml') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            self.setting_data = yaml.load(file, Loader=yaml.FullLoader)

            self.cam_height = int(self.setting_data["cam_height"])
            self.cam_width = int(self.setting_data["cam_width"])
            self.out_path = self.setting_data["out_path"]
            self.cp_path = self.setting_data["cp_path"]
            self.LED_OK = self.setting_data["LED_OK"]
            self.LED_NG = self.setting_data["LED_NG"]
            self.BTN_input = self.setting_data["BTN_INPUT"]

            # Testing
            self.DEBUG = self.setting_data["DEBUG"]
            self.auto_debug = False
            if "sample_img" in self.DEBUG:
                self.DEBUG["cam_width"] = self.cam_width
                self.DEBUG["cam_height"] = self.cam_height
                if self.DEBUG["sample_img"][-4:] != ".png" and self.DEBUG["sample_img"][-4:] != ".jpg":
                    self.auto_debug = True
                    self.timing = time()
            self.TEST_MAMOS = bool(self.setting_data["TEST_MAMOS"])

            if self.TEST_MAMOS:
                from src.mamos import Mamos

                self.mm = Mamos(self.LED_OK, self.LED_NG, self.BTN_input)
            else:
                EpsImagePlugin.gs_windows_binary = self.setting_data["gs"]

        # config canvas
        with open(r'config.yaml') as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)
        self.range_rgb = copy.deepcopy(init_param["drawing"]["range_rgb"])

        # index page
        self.window = window
        self.vid = Vdo(self.DEBUG)
        self.frame = None
        self.mask = None
        self.cur_page = 1
        self.prev_page = 1

        tki.Frame.__init__(self, *args, **kwargs)
        buttonframe = tki.Frame(self)
        container = tki.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        self.p1 = Page1(self, self)
        self.p2 = Page2(self, self)
        self.p3 = Page3(self, self)

        self.p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tki.Button(buttonframe, text="Home", font=("Courier", 44), command=self.move_p1)
        b2 = tki.Button(buttonframe, text="Setting", font=("Courier", 44), command=self.move_p2)
        b3 = tki.Button(buttonframe, text="Drawing", font=("Courier", 44), command=self.move_p3)

        b1.pack(side="right")
        b2.pack(side="right")
        b3.pack(side="right")

        self.canvas_rt = tki.Canvas(self.window, cursor="cross")
        self.create_monitor_canvas()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.update()
        self.p1.show()

    def create_monitor_canvas(self):
        """Create a canvas that can fit the above video source size"""
        self.canvas_rt = tki.Canvas(self.window, cursor="cross")
        self.canvas_rt.bind("<ButtonPress-1>", self.click_rgb)
        self.canvas_rt.bind("<Button-3>", self.undo_rgb)
        self.canvas_rt.place(relx=0.05, rely=0.01)
        self.canvas_rt.config(width=int(self.cam_width * 0.8), height=int(self.cam_height * 0.8))

    def move_p1(self):
        """Move to Page 1"""
        if self.cur_page != 1:
            if self.cur_page == 3:
                self.p1.show(p3=self.p3)
                self.prev_page = self.cur_page
                self.cur_page = 1
                self.create_monitor_canvas()
            else:
                self.p1.show()
                self.prev_page = self.cur_page
                self.cur_page = 1

    def move_p2(self):
        """Move to Page 2"""
        if self.cur_page != 2:
            if self.cur_page == 3:
                self.p1.show(p3=self.p3)
                self.p2.show()
                self.prev_page = self.cur_page
                self.cur_page = 2
                self.create_monitor_canvas()
            else:
                self.p2.show()
                self.prev_page = self.cur_page
                self.cur_page = 2

    def move_p3(self):
        """Move to Page 3"""
        if self.cur_page != 3:
            msg_type = ""
            for mode in self.p1.drawing_data:
                if self.p1.drawing_data[mode]["temp_pol"]:
                    msg_type = "Error"
                    msg = "Need to finish drawing"
                    messagebox.showerror(msg_type, msg)
            if not self.p1.file_path_o:
                msg_type = "Error"
                msg = "No Image"
                messagebox.showerror(msg_type, msg)

            if msg_type != "Error" and self.cur_page != 3:
                self.canvas_rt.destroy()
                self.p3.show(p1=self.p1)
                self.prev_page = self.cur_page
                self.cur_page = 3

    def click_rgb(self, event):
        """Click on video source to check RGB values

        :param event: click event
        :type event: class
        """
        x, y = event.x, event.y
        open_cv_image = np.array(self.mask)
        rgb_min, rgb_max = et.min_max_color(open_cv_image, x, y, self.range_rgb, half_color_dot)
        self.range_rgb.append({
            "point": (x, y),
            "min": rgb_min,
            "max": rgb_max
        })
        txt_range = "Range: " + str(self.range_rgb[-1]["min"]) + " ~ " + str(self.range_rgb[-1]["max"])
        self.p2.lbl_rgb.config(text=txt_range, font=("Courier", 22))

    def undo_rgb(self, event):
        """Right click to undo RGB values

        :param event: click event
        :type event: class
        """
        if self.range_rgb[-1]["point"] is not None:
            del self.range_rgb[-1]
        txt_range = "Range: " + str(self.range_rgb[-1]["min"]) + " ~ " + str(self.range_rgb[-1]["max"])
        if self.range_rgb[-1]["point"] is not None:
            self.p2.lbl_rgb.config(text=txt_range, font=("Courier", 22))
        else:
            self.p2.lbl_rgb.config(text="", font=("Courier", 22))
            self.range_rgb = copy.deepcopy(init_param["drawing"]["range_rgb"])

    def update(self):
        """Real-time update image in canvas"""
        if self.cur_page != 3:
            if self.auto_debug:
                if int(time() - self.timing) > 3:  # todo delay per loop
                    self.p1.snapshot("compare")
                    self.timing = time()
                    self.vid.cur_debug += 1

            if self.TEST_MAMOS:
                if self.mm.output():
                    self.p1.snapshot("compare")

            ret, self.frame, _, self.mask = self.vid.get_frame(self.config, self.p1.raw_data_draw)
            # todo test light calibrate >>, self.p1.save_status
            if ret:
                self.mask = imutils.resize(self.mask, height=int(self.cam_height * 0.8), width=int(self.cam_width * 0.8))
                self.mask = Image.fromarray(self.mask)
                self.p1.tk_photo_line = ImageTk.PhotoImage(image=self.mask)
                self.canvas_rt.delete("all")
                self.canvas_rt.create_image(0, 0, image=self.p1.tk_photo_line, anchor=tki.NW)
                # todo run on RUN mode
                if self.range_rgb[-1]["point"] is not None:
                    for rgb_data in self.range_rgb[1:]:
                        x = rgb_data["point"][0]
                        y = rgb_data["point"][1]
                        self.canvas_rt.create_rectangle(
                            x - half_color_dot, y - half_color_dot, x + half_color_dot, y + half_color_dot, fill='red')
        self.window.after(delay, self.update)

    def exit_handler(self):
        """To run some function when this application was closed"""
        print("Ending ..")
        if self.TEST_MAMOS:
            self.mm.clean()


def toggle_geom(self, event):
    """Geometry of GUI

    :param self: Tkinter class
    :type self: class
    :param event: Geometry event
    :type event: class
    """
    geom = self.master.winfo_geometry()
    print(geom, self._geom)
    self.master.geometry(self._geom)
    self._geom = geom


if __name__ == "__main__":
    root = tki.Tk()
    main = App(root)
    atexit.register(main.exit_handler)
    main.pack(side="top", fill="both", expand=True)

    # Tkinter setting
    pad = 0
    tki.Frame._geom = '200x200+0+0'
    root.geometry("{0}x{1}+0+0".format(
        root.winfo_screenwidth() - pad, root.winfo_screenheight() - pad))
    root.bind('<Escape>', toggle_geom)
    root.title("Tkinter and OpenCV")
    root.resizable(1, 1)
    root.configure(background="#d9d9d9")
    root.mainloop()
