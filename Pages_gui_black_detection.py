# todo config camera bar gui/cv2 in tkinter
# todo clear image in "/output/o_.jpg"
# todo camera moved detection
# todo program slowed when a lot function update realtime ex hue -> Need RUN/STOP Button when start/STOP

"""
check linear line
http://www.webmath.com/_answer.php
Iterporation
https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
"""

import tkinter as tki
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import imutils
import atexit
import yaml

import init_project

init_project.create_folders()

from src import extraction as et
from src.video_capture import MyVideoCapture as vc
from src import logger
from gui import Page1, Page2

from PIL import EpsImagePlugin


# Global variable
half_px = 3


class App(tki.Frame):
    def __init__(self, window, window_title, *args, **kwargs):
        # Project variable
        self.log = logger.GetSystemLogger()

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
            if "sample_img" in self.DEBUG:
                self.DEBUG["cam_width"] = self.cam_width
                self.DEBUG["cam_height"] = self.cam_height
            self.TEST_MAMOS = bool(self.setting_data["TEST_MAMOS"])

            if self.TEST_MAMOS:
                from src.mamos import Mamos

                self.mm = Mamos(self.LED_OK, self.LED_NG, self.BTN_input)
            else:
                EpsImagePlugin.gs_windows_binary = self.setting_data["gs"]

            self.mini_sampling = 4
        # <<<

        # config canvas
        with open(r'config.yaml') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            self.config = yaml.load(file, Loader=yaml.FullLoader)
        # [self.config["t_red"], self.config["t_green"], self.config["t_blue"]]
        self.range_rgb = [{
            "point": None,
            "min": [255, 255, 255],
            "max": [0, 0, 0]
        }]
        self.original_threshold_dist = [0, 0]
        # <<<

        self.window = window
        self.vid = vc(self.DEBUG)
        self.frame = None

        tki.Frame.__init__(self, *args, **kwargs)
        # open video source (by default this will try to open the computer webcam)
        buttonframe = tki.Frame(self)
        container = tki.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        self.p1 = Page1(self, self)
        self.p2 = Page2(self, self)

        self.p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tki.Button(buttonframe, text="Home", font=("Courier", 44), command=self.p1.lift)
        b2 = tki.Button(buttonframe, text="Setting", font=("Courier", 44), command=self.p2.lift)

        b1.pack(side="right")
        b2.pack(side="right")

        # Create a canvas that can fit the above video source size
        self.canvas_rt = tki.Canvas(window, cursor="cross")
        self.canvas_rt.bind("<ButtonPress-1>", self.click_rgb)
        self.canvas_rt.bind("<Button-3>", self.undo_rgb)
        self.canvas_rt.place(relx=0.05, rely=0.01)
        self.canvas_rt.config(width=int(self.cam_width * 0.8), height=int(self.cam_height * 0.8))

        # # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        self.p1.show()

    def click_rgb(self, event):
        x, y = event.x, event.y
        rgb_min, rgb_max = et.min_max_color(self.frame, x, y, self.range_rgb, half_px)
        self.range_rgb.append({
            "point": (x, y),
            "min": rgb_min,
            "max": rgb_max
        })

    def undo_rgb(self, event):
        # x, y = event.x, event.y
        if self.range_rgb[-1]["point"] is not None:
            del self.range_rgb[-1]

    def update(self):
        if self.TEST_MAMOS:
            if self.mm.output():
                self.p1.snapshot("compare")

        ret, self.frame, _, mask = self.vid.get_frame(self.config, self.p1.raw_data_draw)
        if ret:
            mask = imutils.resize(mask, height=int(self.cam_height * 0.8), width=int(self.cam_width * 0.8))
            mask = Image.fromarray(mask)
            self.p1.tk_photo_line = ImageTk.PhotoImage(image=mask)
            self.canvas_rt.create_image(0, 0, image=self.p1.tk_photo_line, anchor=tki.NW)
            # todo run on RUN mode
            if self.range_rgb[-1]["point"] is not None:
                for rgb_data in self.range_rgb[1:]:
                    x = rgb_data["point"][0]
                    y = rgb_data["point"][1]
                    self.canvas_rt.create_rectangle(x - half_px, y - half_px, x + half_px, y + half_px, fill='red')
            if self.p1.raw_data_draw:
                if (self.config["t_width_min"], self.config["t_width_max"]) != self.original_threshold_dist:
                    self.original_threshold_dist = (self.config["t_width_min"], self.config["t_width_max"])
                    self.p1.load_line(self.p1.canvas2, self.p1.raw_data_draw)
        self.window.after(self.delay, self.update)

    def exit_handler(self):
        print("Ending ..")
        if self.TEST_MAMOS:
            self.mm.clean()


def toggle_geom(self, event):
    geom = self.master.winfo_geometry()
    print(geom, self._geom)
    self.master.geometry(self._geom)
    self._geom = geom


if __name__ == "__main__":
    root = tki.Tk()
    main = App(root, "Tkinter and OpenCV")
    atexit.register(main.exit_handler)
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
