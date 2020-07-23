# todo right click to prev draw/original
# todo canvas draw only in image.org

# todo **save draw point
# todo **img processing

import tkinter as tki
import cv2
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import time
import imutils
import datetime


full_w = 1350
camera_h = 250
camera_w = 300
out_path = "output/"

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        # self.window.geometry("1300x700")
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tki.Canvas(window, cursor="cross")
        # self.canvas.place(relx=0.6, rely=0.02, relheight=0.4, relwidth = 0.4)
        self.canvas.config(width=camera_w, height=camera_h)
        self.canvas.pack()

        self.canvas2 = tki.Canvas(window)
        # self.canvas2.place(relx=1.0, rely=0.02, relheight=0.4, relwidth=0.4)

        # >> additional
        self.x = self.y = 0
        self.canvas2.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas2.bind("<B1-Motion>", self.on_move_press)
        self.canvas2.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = []
        self.start_x = None
        self.start_y = None
        # <<

        self.canvas2.config(width=full_w, height=camera_h)
        self.canvas2.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot = tki.Button(window, text="Snapshot", width=50, command=self.snapshot_origin)
        self.btn_snapshot.pack(anchor=tki.CENTER, expand=True)

        self.btn_compare = tki.Button(window, text="Save", width=50, command=self.save_draw)
        self.btn_compare.pack(anchor=tki.CENTER, expand=True)

        self.btn_compare = tki.Button(window, text="Compare", width=50, command=self.snapshot_compare)
        self.btn_compare.pack(anchor=tki.CENTER, expand=True)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tki.NW)

        self.window.after(self.delay, self.update)

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas2.canvasx(event.x)
        self.start_y = self.canvas2.canvasy(event.y)

        # create rectangle if not yet exist
        # if not self.rect:
        self.rect.append(self.canvas2.create_rectangle(self.x, self.y, 1, 1, outline='red'))

    def on_move_press(self, event):
        curX = self.canvas2.canvasx(event.x)
        curY = self.canvas2.canvasy(event.y)

        w, h = self.canvas2.winfo_width(), self.canvas2.winfo_height()
        if event.x > 0.9 * w:
            self.canvas2.xview_scroll(1, 'units')
        elif event.x < 0.1 * w:
            self.canvas2.xview_scroll(-1, 'units')
        if event.y > 0.9 * h:
            self.canvas2.yview_scroll(1, 'units')
        elif event.y < 0.1 * h:
            self.canvas2.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.canvas2.coords(self.rect[-1], self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        pass

    def snapshot(self, mode):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        if ret:
            if mode == "original":
                file_path = out_path + "o_" + filename
                cv2.imwrite(file_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                load_img = Image.open(file_path)
                size = [camera_w, camera_h, 300, 100]
                load_img = load_img.resize((size[0], size[1]), Image.ANTIALIAS)
                self.photo_org = ImageTk.PhotoImage(image=load_img)
                self.canvas2.create_image(size[2], size[3], image=self.photo_org)
            elif mode == "compare":
                file_path = out_path + "c_" + filename
                cv2.imwrite(file_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                load_img = Image.open(file_path)
                size = [camera_w, camera_h, 1000, 100]
                load_img = load_img.resize((size[0], size[1]), Image.ANTIALIAS)
                self.photo_cp = ImageTk.PhotoImage(image=load_img)
                self.canvas2.create_image(size[2], size[3], image=self.photo_cp)

    def snapshot_origin(self):
        self.snapshot("original")

    def snapshot_compare(self):
        self.snapshot("compare")

    def save_draw(self):
        pass


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = imutils.resize(frame, height=camera_h, width=camera_w)
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        # else:
        #     return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


# Create a window and pass it to the Application object
App(tki.Tk(), "Tkinter and OpenCV")
