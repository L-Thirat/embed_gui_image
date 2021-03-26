from gui.page_control import Page
import tkinter as tki
import yaml


class Page2(Page):
    def __init__(self, app, *args, **kwargs):
        """ Page 2 config

        :param app: Tkinter (GUI builder) setup
        :type app: class
        :param args: Tkinter's arguments
        :type args: Optional
        :param kwargs: Tkinter's kwargs arguments
        :type kwargs: Optional
        """
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
        scale_zoom = tki.Scale(self.buttonframe, from_=1, to=2, tickinterval=1, orient=tki.HORIZONTAL,
                               length=(self.winfo_screenwidth() * 0.05), command=self.change_zoom)
        scale_zoom.set(self.app.config["t_zoom"])
        scale_zoom.place(relx=0.58, rely=0.31)

        lbl_blur = tki.Label(self.buttonframe, text="Blur", font=("Courier", 44))
        lbl_blur.place(relx=0.65, rely=0.31)
        scale_blur = tki.Scale(self.buttonframe, from_=1, to=4, tickinterval=1, orient=tki.HORIZONTAL,
                               length=(self.winfo_screenwidth() * 0.14), command=self.change_blur)
        scale_blur.set(self.app.config["t_blur"])
        scale_blur.place(relx=0.753, rely=0.31)

        # Detection tab
        lbl_topic = tki.Label(self.buttonframe, text="Detection", font=("Courier", 55))
        lbl_topic.place(relx=0.57, rely=0.40)

        lbl_space = tki.Label(self.buttonframe, text="Space", font=("Courier", 44))
        lbl_space.place(relx=0.47, rely=0.5)
        scale_space = tki.Scale(self.buttonframe, from_=1, to=self.app.cam_width, tickinterval=100,
                                orient=tki.HORIZONTAL,
                                length=(self.winfo_screenwidth() * 0.5) - pad_half_width, command=self.change_space)
        scale_space.set(self.app.config["t_space"])
        scale_space.place(relx=0.65, rely=0.5)

        lbl_noise = tki.Label(self.buttonframe, text="Noise", font=("Courier", 44))
        lbl_noise.place(relx=0.47, rely=0.6)
        scale_noise = tki.Scale(self.buttonframe, from_=0, to=1000, tickinterval=200, orient=tki.HORIZONTAL,
                                length=(self.winfo_screenwidth() * 0.14), command=self.change_noise)
        scale_noise.set(self.app.config["t_noise"])
        scale_noise.place(relx=0.58, rely=0.6)

        lbl_error = tki.Label(self.buttonframe, text="%", font=("Courier", 44))
        lbl_error.place(relx=0.73, rely=0.6)
        scale_error = tki.Scale(self.buttonframe, from_=0, to=100, tickinterval=20, orient=tki.HORIZONTAL,
                                length=(self.winfo_screenwidth() * 0.14), command=self.change_error)
        scale_error.set(self.app.config["t_error"])
        scale_error.place(relx=0.753, rely=0.6)

        lbl_darkness = tki.Label(self.buttonframe, text="Darkness", font=("Courier", 44))
        lbl_darkness.place(relx=0.47, rely=0.7)
        scale_darkness = tki.Scale(self.buttonframe, from_=0, to=255, tickinterval=51, orient=tki.HORIZONTAL,
                                   length=(self.winfo_screenwidth() * 0.5) - pad_half_width, command=self.change_darkness)
        scale_darkness.set(self.app.config["t_dk"])
        scale_darkness.place(relx=0.65, rely=0.7)

        # save tab
        btn_save = tki.Button(self.buttonframe, font=("Courier", 44), text="Save", command=self.save_config)
        btn_save.place(relx=0.45, rely=0.8)

    def save_config(self):
        """ Save config data to yaml file"""
        print("SAVE: config.yaml")
        with open('config.yaml', 'w') as outfile:
            yaml.dump(self.app.config, outfile, default_flow_style=False)

    def change_darkness(self, val):
        """ Change maximum value of blue color detection"""
        self.app.config["t_dk"] = int(val)

    def change_light(self, val):
        """ Change light config"""
        self.app.config["t_light"] = int(val)

    def change_contrast(self, val):
        """ Change contrast config"""
        self.app.config["t_contrast"] = int(val)

    def change_zoom(self, val):
        """ Change zoom config"""
        self.app.config["t_zoom"] = int(val)

    def change_blur(self, val):
        """ Change blur config"""
        self.app.config["t_blur"] = int(val)

    def change_space(self, val):
        """ Change space detection value"""
        self.app.config["t_space"] = int(val)

    def change_noise(self, val):
        """ Change minimum length of noise detection value"""
        self.app.config["t_noise"] = int(val)

    def change_error(self, val):
        """ Change maximum error config"""
        self.app.config["t_error"] = int(val)
