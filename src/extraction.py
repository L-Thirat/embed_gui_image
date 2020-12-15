import cv2
from scipy import interpolate
import numpy as np
from src import linear_processing as lp


def draw_contour(img, mask):
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    draw_cnt = cv2.drawContours(img, contours[1:], -1, (0, 255, 0), 2)
    return draw_cnt, contours


def contour_selection(contours, img):
    select_contour = []  # todo for check only
    for cnt in contours[1:]:
        len_cont = cv2.arcLength(cnt, -1)
        approx = cv2.approxPolyDP(cnt, 0.02 * len_cont, True)
        x, y, w, h = cv2.boundingRect(approx)
        if len_cont > 25:
            select_contour.append(cnt)
            cv2.putText(img, "" + str(int(len_cont)), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255),
                        2)
            cv2.drawContours(img, cnt, -1, (255, 0, 0), 2)
        # cv2.imshow("img", img)
    return select_contour, img


def detect_error_cnt(contours, raw_data_draw, sampling, t_num_error, t_dist):
    """Get result from comparing image"""
    error_cnt = []
    error_lack = []
    lines = {}

    for key, val in raw_data_draw.items():
        if key != "filename" and key != "area" and key != "ignore":
            # todo https://www.geeksforgeeks.org/solving-linear-regression-in-python/
            start_line = (val["rect"][0], val["rect"][1])
            end_line = (val["rect"][2], val["rect"][3])
            m, c = lp.linear_formula(start_line, end_line)

            sampling_step = (end_line[0] - start_line[0]) / sampling  # points
            x = np.arange(start_line[0], end_line[0], sampling_step)
            y = m * x + c
            f = interpolate.interp1d(x, y)

            xnew = np.arange(start_line[0], end_line[0], sampling_step)
            ynew = f(xnew)  # use interpolation function returned by `interp1d`

            # plt.plot(x, y, 'o', xnew, ynew, '-')
            # plt.show()
            sampling_point = {(x, y): 0 for x, y in zip(xnew, ynew)}
            lines[(start_line, end_line)] = {"m": m, "c": c, "sampling": sampling_point}

    # find error from matching distance
    for cnt in contours:
        matching = False

        start_point, end_point = lp.find_start_end(cnt)
        # find matching line
        for line in lines:
            start_line = line[0]
            end_line = line[1]

            num_error = 0
            for p in cnt:
                x, y = p[0][0], p[0][1]
                dist = lp.point2line_match((x, y), start_line, end_line)
                if dist > t_dist:
                    num_error += 1

                # find error from lacking point (loop in sampling of matching line)
                for point in lines[line]["sampling"]:
                    (X_comp, Y_comp) = point
                    if lines[line]["sampling"][(X_comp, Y_comp)] == 0:
                        dist = lp.find_distance((X_comp, Y_comp), (x, y))
                        if dist < t_dist:
                            lines[line]["sampling"][(X_comp, Y_comp)] = 1

            if num_error < t_num_error:
                matching = True
                break
            else:
                for point in lines[line]["sampling"]:
                    (X_comp, Y_comp) = point
                    lines[line]["sampling"][(X_comp, Y_comp)] = 0

        if not matching:
            error_cnt.append((start_point, end_point))

    # summary error lack
    for line in lines:
        if 0 in lines[line]["sampling"].values():
            cnt = []
            for key, val in lines[line]["sampling"].items():
                if val == 0:
                    cnt.append([key])
            if len(cnt) > 1:
                start_point, end_point = lp.find_start_end(cnt)
                error_lack.append((start_point[0], start_point[1], end_point[0], end_point[1]))
            else:
                error_lack.append(cnt[0][0])
    return error_cnt, error_lack
