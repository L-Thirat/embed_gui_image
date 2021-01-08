import cv2
from scipy import interpolate
import numpy as np
from src import linear_processing as lp
from shapely.geometry import LineString, Point, Polygon
import shapely.speedups
shapely.speedups.enable()

cv2ver = cv2.__version__
if "3." in cv2ver:
    cv2ver = 3
else:
    cv2ver = 4


def draw_contour(img, mask):
    if cv2ver == 3:
        # https://qiita.com/anyamaru/items/fd3d894966a98098376c
        mask, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    draw_cnt = cv2.drawContours(img, contours[1:], -1, (0, 255, 0), 2)
    return draw_cnt, contours


def contour_selection(contours, img, noise_len):
    select_contour = []  # todo for check only
    for cnt in contours[1:]:
        len_cont = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * len_cont, True)
        x, y, w, h = cv2.boundingRect(approx)
        if len_cont > noise_len:
            select_contour.append(cnt)
            cv2.putText(img, "" + str(int(len_cont)), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255),
                        2)
            cv2.drawContours(img, cnt, -1, (255, 0, 0), 2)
        # cv2.imshow("img", img)
    return select_contour, img


def error_line(cnt, crop_area):
    error = []
    for ps in cnt:
        if ps:
            if len(ps) > 1:
                if LineString([(ps[0][0], ps[0][1]), (ps[-1][0], ps[-1][1])]).intersects(Polygon(crop_area)):
                    error.append((ps[0][0], ps[0][1], ps[-1][0], ps[-1][1]))
            else:
                if Point(ps[0][0], ps[0][1]).within(Polygon(crop_area)):
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
        x1, y1, x2, y2 = lp.length2points((val[0], val[1]), (val[2], val[3]), t_width_max)
        start_line = (x1, y1)
        end_line = (x2, y2)
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
    match_cnt = {}
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
                # dist = lp.point2line_match((x, y), start_line, end_line)
                # if (dist >= t_width_min) and (dist <= t_width_max):
                if t_width_min < t_width_max:
                    sample_rect = lp.line2rect(start_line, end_line, t_width_max)
                    point_inside = False
                    if t_width_min:
                        inside_sample_rect = lp.line2rect(start_line, end_line, t_width_min)
                        point_inside = Point(x, y).within(Polygon(inside_sample_rect))
                    if Point(x, y).within(Polygon(sample_rect)) and not point_inside:
                        matching = True
                        if line not in match_cnt:
                            match_cnt[line] = [cnt]
                        else:
                            if cnt not in match_cnt[line]:
                                match_cnt[line].append(cnt)
                        break
            if not matching:
                num_error += 1
        if (num_error * 100) / len(cnt) > t_error:
            error_over.append((start_point, end_point))

    # find matching line
    for line in lines:
        not_match_cnt = [[]]
        matching_count = 0
        prev_p = None

        for point in lines[line]:
            matching = False
            if prev_p:
                if line in match_cnt:
                    sample_rect = lp.line2rect(prev_p, point, t_space)
                    for cnt in match_cnt[line]:
                        poly_cnt = [(item[0][0], item[0][1]) for item in cnt]
                        if Polygon(poly_cnt).intersects(Polygon(sample_rect)):
                            matching_count += 1
                            if not_match_cnt[-1]:
                                not_match_cnt.append([])
                            matching = True
                            break

                if not matching:
                    if not not_match_cnt[-1]:
                        not_match_cnt[-1].append(prev_p)
                    not_match_cnt[-1].append(point)
            prev_p = point
        not_match_cnt.append([])

        if matching_count != len(lines[line]):
            error_under = error_under + error_line(not_match_cnt, raw_data_draw["area"])

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
