# Importing all necessary libraries
import cv2
import os

# Read the video from specified path
dir_file = "frame/"
vdo_dir = "frame/video/"
for filename in os.listdir(vdo_dir):
    # filename = "2021-02-12_121437_IN4"
    if "mp4" in filename and "IN4" in filename:
        cam = cv2.VideoCapture(vdo_dir + filename)

        try:

            # creating a folder named data
            if not os.path.exists(vdo_dir):
                os.makedirs(vdo_dir)

            # if not created then raise error
        except OSError:
            print('Error: Creating directory of data')

        # frame
        currentframe = 0
        select_frame = 5  # max 120

        while True:

            # reading from frame
            ret, frame = cam.read()

            if ret:
                if currentframe == select_frame:
                    # if video is still left continue creating images
                    name = './frame/frame_' + filename[:-4] + '.jpg'
                    print('Creating...' + name)

                    # writing the extracted images
                    cv2.imwrite(name, frame)

                    # increasing counter so that it will
                    # show how many frames are created
            else:
                break
            currentframe += 1

        # Release all space and windows once done
        cam.release()
        cv2.destroyAllWindows()
