# todo right click to prev draw/original
# todo canvas draw only in image.org
# todo config camera bar gui/cv2

# **Importance**
# todo ** tinkboard install

import tkinter as tki
from tkinter import filedialog
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
    def __init__(self, window, window_title, video_source=0):
        self.file_path_o = ""
        self.file_path_c = ""

        # Create Control Bar
        cv2.namedWindow("Parameters")
        cv2.resizeWindow("Parameters", 640, 240)
        cv2.createTrackbar("Threshold1", "Parameters", 42, 255, self.empty)
        cv2.createTrackbar("Threshold2", "Parameters", 0, 255, self.empty)
        cv2.createTrackbar("Area", "Parameters", 100, 60000, self.empty)

        self.window = window
        # self.window.geometry("1300x700")
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

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

        self.load_filename = None
        self.browsebutton = tki.Button(window, text="Browse", width=50, command=self.browsefunc)
        self.browsebutton.pack(anchor=tki.CENTER, expand=True)

        self.pathlabel = tki.Label(window)
        self.pathlabel.pack()

        self.btn_compare = tki.Button(window, text="Compare", width=50, command=self.snapshot_compare)
        self.btn_compare.pack(anchor=tki.CENTER, expand=True)

        self.btn_reset = tki.Button(window, text="Reset", width=50, command=self.reset)
        self.btn_reset.pack(anchor=tki.CENTER, expand=True)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def empty(self, a):
        pass

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tki.NW)

        self.window.after(self.delay, self.update)

    def reset(self):
        self.canvas2.delete("all")

        self.canvas3.delete("all")

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
        self.data_draw[self.count_draw] = {"rect": [self.start_x, self.start_y, curX, curY]}

    def snapshot(self, mode):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        if ret:
            if mode == "original":
                self.file_path_o = out_path + "o_" + filename
                cv2.imwrite(self.file_path_o, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_o = Image.open(self.file_path_o)
                size = [camera_w, camera_h, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.photo_org, anchor=tki.NW)
            elif mode == "compare":
                self.file_path_c = out_path + "c_" + filename
                cv2.imwrite(self.file_path_c, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.load_img_cp = Image.open(self.file_path_c)
                size = [camera_w, camera_h, 0, 0]
                self.load_img_cp = self.load_img_cp.resize((size[0], size[1]), Image.ANTIALIAS)
                cp_result = self.detect_compare()
                print(cp_result)
                self.photo_cp = ImageTk.PhotoImage(image=self.load_img_cp)
                self.canvas3.create_image(size[2], size[3], image=self.photo_cp, anchor=tki.NW)
                self.load_rect(self.canvas3, self.load_draw, cp_result)
                self.load_draw = {}

    def load_rect(self, cvs, data, result=None):
        for key, val in data.items():
            if result:
                color = result[key]
            else:
                color = "red"
            cvs.create_rectangle(val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3], outline=color)
            cvs.create_text((val["rect"][2], val["rect"][3]), text=key, font=('Impact', -15), fill="yellow")

    def snapshot_origin(self):
        self.snapshot("original")

    def snapshot_compare(self):
        self.snapshot("compare")

    def save_draw(self):
        self.count_draw = 0
        for key, val in self.data_draw.items():
            image_area = self.load_img_o.crop((val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3]))
            open_cv_image = np.array(image_area)
            imgDil = self.image_preprocess(open_cv_image)
            cv2.imshow("result", imgDil)
            cv2.imwrite("test.jpg", imgDil)
            data_result = self.getContours(imgDil)
            if data_result:
                x, y, area, points = data_result
                # print(x, y, area, points)
                # todo use other value ?
                self.data_draw[key]["area"] = area
                self.data_draw[key]["filename"] = self.file_path_o

        # todo need test
        data = json.dumps(self.data_draw)
        with open('data/data_%s.json' % self.file_path_o[:-4].replace("output/", ""), 'w') as fp:
            fp.write(data)
        print("SAVE !")
        self.data_draw = {}

    def detect_compare(self):
        result = {}
        if self.load_filename:
            with open(self.load_filename, 'r') as fp:
                self.load_draw = json.load(fp)
        else:
            try:
                with open('data/data_%s.json' % self.file_path_o[:-4].replace("output/", ""), 'r') as fp:
                    self.load_draw = json.load(fp)
            except Exception as e:
                raise e
        for key, val in self.load_draw.items():
            # print(val)
            image_area = self.load_img_cp.crop((val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3]))
            open_cv_image = np.array(image_area)
            imgDil = self.image_preprocess(open_cv_image)
            cv2.imwrite("test_cp.jpg", imgDil)
            data_result = self.getContours(imgDil)

            image_o_area = self.load_img_o.crop(
                (val["rect"][0], val["rect"][1], val["rect"][2], val["rect"][3]))  # // = image_o fill
            image_o_area = np.array(image_o_area)
            image_cp_area = np.array(image_area)
            score = self.cp_similarity(image_o_area, image_cp_area)
            print(score)
            if data_result:
                x, y, area, points = data_result
                thershold_percent = 10
                thershold_score = 50
                if (score > thershold_score) and ((abs(area - self.load_draw[key]["area"]) * 100) / self.load_draw[key]["area"] < thershold_percent):
                    # print("True", key, area, self.load_draw[key]["area"])
                    print("item %s => " % key + "True")
                    result[key] = "green"
                else:
                    print("item %s => " % key + "False")
                    result[key] = "red"
            else:
                print("item %s => " % key + "False")
                result[key] = "red"

        return result

    def browsefunc(self):
        self.load_filename = filedialog.askopenfilename()
        self.pathlabel.config(text=self.load_filename)
        if self.load_filename:
            with open(self.load_filename, 'r') as fp:
                self.load_draw = json.load(fp)

                # load img
                self.load_img_o = Image.open(self.load_draw["1"]["filename"])
                size = [camera_w, camera_h, 0, 0]
                self.load_img_o = self.load_img_o.resize((size[0], size[1]), Image.ANTIALIAS)
                self.photo_org = ImageTk.PhotoImage(image=self.load_img_o)
                self.canvas2.create_image(size[2], size[3], image=self.photo_org, anchor=tki.NW)

                # load draw
                self.load_rect(self.canvas2, self.load_draw)

    # >> image processing
    def cp_similarity(self, original, image_to_compare):
        # 1) Check if 2 images are equals
        print(original.shape, image_to_compare.shape)
        if original.shape == image_to_compare.shape:
            print("The images have same size and channels")
            difference = cv2.subtract(original, image_to_compare)
            b, g, r = cv2.split(difference)

            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                print("The images are completely Equal")
            else:
                print("The images are NOT equal")

        # 2) Check for similarities between the 2 images

        sift = cv2.xfeatures2d.SIFT_create()
        kp_1, desc_1 = sift.detectAndCompute(original, None)
        kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)

        index_params = dict(algorithm=0, trees=5)
        search_params = dict()
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(desc_1, desc_2, k=2)

        good_points = []
        ratio = 0.6
        for m, n in matches:
            if m.distance < ratio * n.distance:
                good_points.append(m)
        return (len(good_points)*100) / len(matches)

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
        threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
        threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
        imgCanny = cv2.Canny(imgGray, threshold1, threshold2)  # 255 # todo create tuning bar gui
        kernel = np.ones((5, 5))
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

        return imgDil

    # << image processing


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
for i in range(5):
    try:
        cap = cv2.VideoCapture(i)
        # Check whether user selected camera is opened successfully.
        if not (cap.isOpened()):
            pass
        else:
            App(tki.Tk(), "Tkinter and OpenCV", video_source=i)
    except:
        pass
