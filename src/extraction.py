import cv2
from scipy import interpolate
import numpy as np
from src import linear_processing as lp

cv2ver = cv2.__version__
if "3." in cv2ver:
    cv2ver = 3
else:
    cv2ver = 4


def draw_contour(img, mask):
    if cv2ver == 3:
        mask, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    draw_cnt = cv2.drawContours(img, contours[1:], -1, (0, 255, 0), 2)
    return draw_cnt, contours


def contour_selection(contours, img):
    select_contour = []  # todo for check only
    for cnt in contours[1:]:
        len_cont = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * len_cont, True)
        x, y, w, h = cv2.boundingRect(approx)
        if len_cont > 25:
            select_contour.append(cnt)
            cv2.putText(img, "" + str(int(len_cont)), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255),
                        2)
            cv2.drawContours(img, cnt, -1, (255, 0, 0), 2)
        # cv2.imshow("img", img)
    return select_contour, img


def error_line(match_cnt, over_cnt):
    error = []
    for ps in match_cnt:
        checkpoint = True
        for over in over_cnt:
            if len(ps) > 1:
                if (over[0][0] < ps[0][0]) and (over[0][1] < ps[0][1]) and (over[1][0] > ps[-1][0]) and (
                        over[1][1] > ps[-1][1]):
                    checkpoint = False
                    break
            elif len(ps) == 1:
                if (over[0][0] < ps[0][0]) and (over[0][1] < ps[0][1]):
                    checkpoint = False
                    break
        if checkpoint:
            if len(ps) > 1:
                error.append((ps[0][0], ps[0][1], ps[-1][0], ps[-1][1]))
            elif len(ps) == 1:
                error.append((ps[0][0], ps[0][1]))
    return error


def detect_error_cnt(contours, raw_data_draw, config):
    """Get result from comparing image"""
    t_error = config["t_error"]
    t_width_min = config["t_width_min"]
    t_width_max = config["t_width_max"]
    t_space = config["t_space"]

    error_over = []
    error_under = []
    lines = {}

    for val in raw_data_draw["draws"].values():
        # https://www.geeksforgeeks.org/solving-linear-regression-in-python/
        start_line = (val[0], val[1])
        end_line = (val[2], val[3])
        m, c = lp.linear_formula(start_line, end_line)

        dx, dy = lp.diff_xy(start_line[0], start_line[1], end_line[0], end_line[1], t_space)
        if end_line[0] - start_line[0] != 0:
            x = np.arange(start_line[0], end_line[0], dx)
            y = m * x + c
        else:
            y = np.arange(start_line[1], end_line[1], dy)
            x = (y - c) / m
        f = interpolate.interp1d(x, y)
        xnew = np.arange(start_line[0], end_line[0], dx)
        ynew = f(xnew)  # use interpolation function returned by `interp1d`
        # plt.plot(x, y, 'o', xnew, ynew, '-')
        # plt.show()
        sampling_point = [(x, y) for x, y in zip(xnew, ynew)]
        lines[(start_line, end_line)] = sampling_point

    # find over contour
    for cnt in contours:
        start_point, end_point = lp.find_start_end(cnt)
        num_error = 0
        for p in cnt:
            matching = False
            matching_count = 0
            x, y = p[0][0], p[0][1]

            # find matching line
            for line in lines:
                start_line = line[0]
                end_line = line[1]
                dist = lp.point2line_match((x, y), start_line, end_line)
                if (dist >= t_width_min) and (dist <= t_width_max):
                    matching_count += 1
                    matching = True
                    break

            if not matching:
                num_error += 1
        if (num_error * 100) / len(cnt) > t_error:
            error_over.append((start_point, end_point))

    # find matching line
    not_match_cnt = [[]]
    for line in lines:
        matching_count = 0
        for point in lines[line]:
            matching = False
            (X_comp, Y_comp) = point
            for cnt in contours:
                for p in cnt:
                    x, y = p[0][0], p[0][1]
                    dist = lp.find_distance((X_comp, Y_comp), (x, y))
                    if (dist >= t_width_min) and (dist <= t_width_max):
                        matching_count += 1
                        if not_match_cnt[-1]:
                            not_match_cnt.append([])
                            matching = True
                        break
                else:
                    continue
                break
            if not matching:
                not_match_cnt[-1].append((X_comp, Y_comp))
        not_match_cnt.append([])
        if matching_count != len(lines[line]):
            error_under = error_under + error_line(not_match_cnt, over_cnt=error_over)

    return error_over, error_under


def min_max_color(frame, x, y, range_rgb, half_px):
    base_min_rgb = range_rgb[-1]["min"]
    base_max_rgb = range_rgb[-1]["max"]
    for h in frame[y - half_px:y + half_px]:
        for w in h[x - half_px:x + half_px]:
            for i in range(3):
                if w[i] < base_min_rgb[i]:
                    base_min_rgb[i] = w[i]
            for i in range(3):
                if w[i] > base_max_rgb[i]:
                    base_max_rgb[i] = w[i]
    return base_min_rgb, base_max_rgb
