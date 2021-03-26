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

from src import extraction as et
from gui.page_control import Page
from gui.drawing_control import DrawingPage
import init_project
from init_project import init_dir

from gui import Page1

# Load init params
init_param = init_project.init_param()


class Page3(DrawingPage):
    def __init__(self, app, *args, **kwargs):
        """ Page 3 config

        :param app: Tkinter (GUI builder) setup
        :type app: class
        :param args: Tkinter's arguments
        :type args: Optional
        :param kwargs: Tkinter's kwargs arguments
        :type kwargs: Optional
        """
        size = (960, 720, 0, 0)
        DrawingPage.__init__(self, app, size, "p3", *args, **kwargs)

        self.canvas2.place(relx=0.05, rely=0.1)
        self.canvas2.config(width=size[0], height=size[1])

        self.btn_mode_detect.place(relx=0.74, rely=0.18)
        self.btn_mode_inside.place(relx=0.81, rely=0.18)
        self.btn_mode_area.place(relx=0.88, rely=0.18)
