import cv2
import numpy as np


for i in range(10):
    vid = cv2.VideoCapture(i)
    if vid.isOpened():
        break

while True:
    # read image
    ret, img = vid.read()
    # img = cv2.imread("WIN_20201210_10_12_37_Pro.jpg")

    # convert img to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # do adaptive threshold on gray image
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 25)

    # make background of input white where thresh is white
    result = img.copy()
    result[thresh==255] = (255,255,255)

    # write results to disk
    # cv2.imwrite("math_diagram_threshold.jpg", thresh)
    # cv2.imwrite("math_diagram_processed.jpg", result)

    # display it
    cv2.imshow("THRESHOLD", thresh)
    # cv2.imshow("RESULT", result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
vid.release()
cv2.destroyAllWindows()