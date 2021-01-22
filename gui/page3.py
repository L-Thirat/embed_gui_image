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
import init_project
from init_project import init_dir

from gui import Page1

# Load init params
init_param = init_project.init_param()

FULL_SIZE = (960, 720)


class Page3(Page):
    def __init__(self, app, *args, **kwargs):
        """ Page 3 config

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

        self.p1 = self.app.p1

        Page.__init__(self, *args, **kwargs)
        self.buttonframe = tki.Frame(self)
        self.buttonframe.pack(side="top", fill="both", expand=True)

        # Drawing cv
        self.canvas2 = tki.Canvas(self.buttonframe, cursor="cross")
        self.canvas2.place(relx=0.05, rely=0.1)
        self.canvas2.config(width=FULL_SIZE[0], height=FULL_SIZE[1])
        print("p3")
