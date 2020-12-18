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


def detect_error_cnt(contours, raw_data_draw, sampling, config):
    """Get result from comparing image"""
    t_error = config["t_error"]
    t_width_min = config["t_width_min"]
    t_width_max = config["t_width_max"]
    t_space = config["t_space"]

    error_cnt = []
    error_lack = []
    start2end_match_cnt = {}
    lines = {}

    for key, val in raw_data_draw.items():
        if key != "filename" and key != "area" and key != "ignore":
            # https://www.geeksforgeeks.org/solving-linear-regression-in-python/
            start_line = (val["rect"][0], val["rect"][1])
            end_line = (val["rect"][2], val["rect"][3])
            m, c = lp.linear_formula(start_line, end_line)

            if end_line[0] - start_line[0] != 0:
                sampling_step = (end_line[0] - start_line[0]) / sampling
                x = np.arange(start_line[0], end_line[0], sampling_step)
                y = m * x + c
            else:
                sampling_step = (end_line[1] - start_line[1]) / sampling
                y = np.arange(start_line[1], end_line[1], sampling_step)
                x = (y - c)/m
            f = interpolate.interp1d(x, y)

            xnew = np.arange(start_line[0], end_line[0], sampling_step)
            ynew = f(xnew)  # use interpolation function returned by `interp1d`

            # plt.plot(x, y, 'o', xnew, ynew, '-')
            # plt.show()
            sampling_point = {(x, y): 0 for x, y in zip(xnew, ynew)}
            lines[(start_line, end_line)] = sampling_point

    # find matching line
    for line in lines:
        start2end_match_cnt[line] = []
        for point in lines[line]:
            (X_comp, Y_comp) = point
            for cnt in contours:
                start_point, end_point = lp.find_start_end(cnt)
                for p in cnt:
                    x, y = p[0][0], p[0][1]
                    if lines[line][(X_comp, Y_comp)] == 0:
                        dist = lp.find_distance((X_comp, Y_comp), (x, y))
                        if (dist >= t_width_min) and (dist <= t_width_max):
                            lines[line][(X_comp, Y_comp)] = 1
                            if (start_point, end_point) not in start2end_match_cnt[line]:
                                start2end_match_cnt[line].append((start_point, end_point))
                            break
                else:
                    continue
                break

    # summary error lack
    for line in start2end_match_cnt:
        space = None
        space_point = ()
        for i, cnt1 in enumerate(start2end_match_cnt[line]):
            for cnt2 in start2end_match_cnt[line]:
                if cnt1 != cnt2:
                    dist = lp.find_distance(cnt1[1], cnt2[0])
                    if space is None:
                        space = dist
                        space_point = (cnt1[1][0], cnt1[1][1], cnt2[0][0], cnt2[0][1])
                    else:
                        if lp.find_distance(cnt1[1], cnt2[0]) < space:
                            space = dist
                            space_point = (cnt1[1][0], cnt1[1][1], cnt2[0][0], cnt2[0][1])
        if space:
            if space > t_space:
                error_lack.append(space_point)

    # find over contour
    for cnt in contours:
        start_point, end_point = lp.find_start_end(cnt)
        num_error = 0
        for p in cnt:
            matching = False
            x, y = p[0][0], p[0][1]

            # find matching line
            for line in lines:
                start_line = line[0]
                end_line = line[1]
                dist = lp.point2line_match((x, y), start_line, end_line)
                if (dist >= t_width_min) and (dist <= t_width_max):
                    matching = True
                    break
                # else:
                #     print(print(dist))

            if not matching:
                num_error += 1

        if (num_error*100)/len(cnt) > t_error:
            error_cnt.append((start_point, end_point))

    return error_cnt, error_lack
