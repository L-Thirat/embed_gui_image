import math
from numpy import ones, vstack
from numpy.linalg import lstsq


def find_distance(p1, p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))


def find_start_end(cnt):
    # start_point, start_dis = (), find_distance((camera_w, camera_h), (0, 0))
    start_point, start_dis = (), find_distance((640, 480), (0, 0))
    end_point, end_dis = (), 0
    for cord in cnt:
        cur_point = (cord[0][0], cord[0][1])
        cur_distance = find_distance(cur_point, (0, 0))
        if cur_distance < start_dis:
            start_point, start_dis = cur_point, cur_distance
        if cur_distance > end_dis:
            end_point, end_dis = cur_point, cur_distance
    return start_point, end_point


def linear_formula(p1, p2):
    o_points = [p1, p2]
    x_coords, y_coords = zip(*o_points)
    A = vstack([x_coords, ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords, rcond=-1)[0]
    # print("Line Solution is y = {m}x + {c}".format(m=m, c=c))
    return m, c


def diff_xy(x1, y1, x2, y2, l):
    red = math.atan(abs(y2 - y1) / abs(x2 - x1))
    dx = math.cos(red) * l
    dy = math.sin(red) * l
    return dx, dy


def length2points(p1, p2, l):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    dx, dy = diff_xy(x1, y1, x2, y2, l)

    if x1 < x2:
        new_p1x = p1[0] - dx
        new_p2x = p2[0] + dx
    else:
        new_p1x = p1[0] + dx
        new_p2x = p2[0] - dx

    if y1 < y2:
        new_p1y = p1[1] - dy
        new_p2y = p2[1] + dy
    else:
        new_p1y = p1[1] + dy
        new_p2y = p2[1] - dy

    return new_p1x, new_p1y, new_p2x, new_p2y


# > find
def dist2(start, end):
    return (start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2


def point2line_match(p, start, end):
    # https://stackoverfloend.com/questions/849211/shortest-distance-betendeen-a-point-and-a-line-segment
    l2 = dist2(start, end)
    # distToSegmentSquared
    if l2 == 0:
        return dist2(p, start)
    t = ((p[0] - start[0]) * (end[0] - start[0]) + (p[1] - start[1]) * (end[1] - start[1])) / l2
    t = max(0, min(1, t))
    dis2sag_squad = dist2(p, [start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])])
    return math.sqrt(dis2sag_squad)
