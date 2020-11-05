# todo right click to prev draw/original
# todo canvas draw only in image.org

# **Importance**
# todo **save draw point -> file.txt
# todo **img processing
# todo ** tinkboard install

import tkinter as tki
import cv2
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import time
import imutils
import datetime
import numpy as np
import json


full_w = 1350
camera_h = 250
camera_w = 300
out_path = "output/"

class App:
    def __init__(self, window, window_title):
        self.window = window
        # self.window.geometry("1300x700")
        self.window.title(window_title)
        #self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture()

        # Create a canvas that can fit the above video source size
        self.canvas = tki.Canvas(window)
        self.canvas.config(width=camera_w, height=camera_h)
        self.canvas.pack()

        self.canvas2 = tki.Canvas(window, cursor="cross")
        # >> additional
        self.x = self.y = 0
        self.count_draw = 0
        self.data_draw = {}
        self.canvas2.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas2.bind("<B1-Motion>", self.on_move_press)
        self.canvas2.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = []
        self.start_x = None
        self.start_y = None
        # <<
        self.canvas2.config(width=camera_w, height=camera_h)
        self.canvas2.pack()

        self.canvas3 = tki.Canvas(window)
        self.canvas3.config(width=camera_w, height=camera_h)
        self.canvas3.pack()

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
        self.count_draw += 1
        curX = self.canvas2.canvasx(event.x)
        curY = self.canvas2.canvasy(event.y)
        self.data_draw[self.count_draw] = {"rect" : [self.start_x, self.start_y, curX, curY]}

    def snapshot(self, mode):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        if ret:
            if mode == "original":
                file_path = out_path + "o_" + filename
                cv2.imwrite(file_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_o = Image.open(file_path)
                size = [camera_w, camera_h, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.photo_org, anchor=tki.NW)
            elif mode == "compare":
                file_path = out_path + "c_" + filename
                cv2.imwrite(file_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_cp = Image.open(file_path)
                size = [camera_w, camera_h, 0, 0]
                self.load_img_cp = self.load_img_cp.resize((size[0], size[1]), Image.ANTIALIAS)
                self.detect_compare()
                self.photo_cp = ImageTk.PhotoImage(image=self.load_img_cp)
                self.canvas3.create_image(size[2], size[3], image=self.photo_cp, anchor=tki.NW)

    def snapshot_origin(self):
        self.snapshot("original")

    def snapshot_compare(self):
        self.snapshot("compare")

    def save_draw(self):
        for key, val in self.data_draw.items():
            # print(val)
            image_area = self.load_img_o.crop((val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3]))
            open_cv_image = np.array(image_area)
            imgDil = self.image_preprocess(open_cv_image)
            cv2.imwrite("test.jpg",imgDil)
            data_result = self.getContours(imgDil)
            if data_result:
                x, y, area, points = data_result
                # print(x, y, area, points)
                # todo use other value ?
                self.data_draw[key]["area"] = area

        data = json.dumps(self.data_draw)
        with open('app.json', 'w') as fp:
            json.dump(data, fp)
        print("SAVE !")

    def detect_compare(self):
        for key, val in self.data_draw.items():
            # print(val)
            image_area = self.load_img_cp.crop((val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3]))
            open_cv_image = np.array(image_area)
            imgDil = self.image_preprocess(open_cv_image)
            cv2.imwrite("test_cp.jpg",imgDil)
            data_result = self.getContours(imgDil)
            if data_result:
                x, y, area, points = data_result
                thershold_percent = 10
                if (abs(area - self.data_draw[key]["area"]) * 100) / self.data_draw[key]["area"] < thershold_percent:
                    # print("True", key, area, self.data_draw[key]["area"])
                    print("item %d => " % key + "True")
                else:
                    print("item %d => " % key + "False")
            else:
                print("item %d => " % key + "False")

    # >> image processing
    def getContours(self, img):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # >>> Find original position
        # item_area = 10000  # minimum area of item
        original_x, original_y = 0, 0
        original_area = 0
        if len(contours) == 1:
            # todo fix not check from len
            for cnt in contours:
                area = cv2.contourArea(cnt)

                # if area > item_area:
                M = cv2.moments(cnt)

                original_area = area
                original_x = int(M['m10'] / M['m00'])
                original_y = int(M['m01'] / M['m00'])

                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            return original_x, original_y, original_area, len(approx)

    def image_preprocess(self, img):
        imgContour = img.copy()
        imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
        # threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
        # threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
        imgCanny = cv2.Canny(imgGray, 42, 0)  # 255 # todo create tuning bar gui
        kernel = np.ones((5, 5))
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
        return imgDil

    # << image processing



class MyVideoCapture:
    def __init__(self):
        # Open the video source
        for i in range(10):
            self.vid = cv2.VideoCapture(i)
            if not self.vid.isOpened():
                pass
            #raise ValueError("Unable to open video source", video_source)
            else:
                break
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
