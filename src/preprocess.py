import cv2
import numpy as np


def apply_brightness_contrast(input_img, brightness=0, contrast=0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0 and (127 * (131 - contrast)) != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf


def brightness(img, t_light, t_contrast):
    img = apply_brightness_contrast(img, -t_light, t_contrast)
    return img


def hue(img, t_red, t_green, t_blue):
    # define range of a color in HSV
    lower_hue = np.array([0, 0, 0])
    upper_hue = np.array([t_red, t_green, t_blue])
    mask = cv2.inRange(img, lower_hue, upper_hue)

    (T, mask) = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY_INV)

    # ## (2) Morph-op to remove noise
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    # morphed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def crop_img(img, area):
    # contours = [np.array([[333, 147], [320, 329], [361, 464], [411, 425], [382, 164]])]
    contours = [np.array(area)]
    fill_color = [255, 255, 255]  # any BGR color value to fill with
    mask_value = 1  # 1 channel white (can be any non-zero uint8 value)

    stencil = np.zeros(img.shape[:-1]).astype(np.uint8)
    cv2.fillPoly(stencil, contours, mask_value)

    sel = stencil != mask_value
    img[sel] = fill_color

    return img
