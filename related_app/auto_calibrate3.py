import cv2
import numpy as np
from matplotlib import pyplot as plt

BASE_ALPHA = 3.072289156626506
BASE_BETA = -144.3975903614458

def convertScale(img, alpha, beta):
    """Add bias and gain to an image with saturation arithmetics. Unlike
    cv2.convertScaleAbs, it does not take an absolute value, which would lead to
    nonsensical results (e.g., a pixel at 44 with alpha = 3 and beta = -210
    becomes 78 with OpenCV, when in fact it should become 0).
    """

    new_img = img * alpha + beta
    new_img[new_img < 0] = 0
    new_img[new_img > 255] = 255
    return new_img.astype(np.uint8)


# Automatic brightness and contrast optimization with optional histogram clipping
def automatic_brightness_and_contrast(image, clip_hist_percent=25):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cur_hsv = 255 - int(hsv[-1][-1][-1])
    print(cur_hsv)


image = cv2.imread('auto_result3.png')
hist = (cv2.calcHist([image],[0],None,[256],[0,256]))
plt.plot(hist)
plt.xlim([250, 255])
plt.show()
# automatic_brightness_and_contrast(image)
# print('alpha', alpha)
# print('beta', beta)
# cv2.imshow('auto_result2', auto_result)
# cv2.imwrite('auto_result3.png', auto_result)
# cv2.imshow('image', image)
# cv2.waitKey()