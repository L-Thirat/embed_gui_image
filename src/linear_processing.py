import math
from numpy import ones, vstack
from numpy.linalg import lstsq


def find_distance(p1, p2):
    """Find distance between 2 points

    :param p1: point
    :type p1: tuple
    :param p2: point
    :type p2: tuple
    :return: Distance between 2 points
    :rtype: float
    """
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))


def dist2(p1, p2):
    """Find square of distance between 2 points

    :param p1: point
    :type p1: tuple
    :param p2: point
    :type p2: tuple
    :return: Square of distance between 2 points
    :rtype: float, int
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def find_start_end(cnt):
    """Find start-end point from contour data

    :param cnt: list
    :type cnt: class(numpy.ndarray)
    :return: start point, end point
    :rtype: (int, float), (int, float)
    """
    # todo start_point, start_dis = (), find_distance((camera_w, camera_h), (0, 0))
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
    """"Find linear formula from 2 points

    :param p1: point
    :type p1:tuple
    :param p2:point
    :type p2: tuple
    :return: slope, constant
    :rtype: (int, float), (int, float)
    """
    o_points = [p1, p2]
    x_coords, y_coords = zip(*o_points)
    A = vstack([x_coords, ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords, rcond=-1)[0]
    return m, c


def point2line_match(p, start, end):
    """Find minimum distance between point-line

    :param p: point
    :type p: tuple
    :param start: start point
    :type start: tuple
    :param end: end point
    :type end: tuple
    :return: Minimum distance between point-line
    :rtype: float
    """
    # https://stackoverfloend.com/questions/849211/shortest-distance-betendeen-a-point-and-a-line-segment
    l2 = dist2(start, end)
    # distToSegmentSquared
    if l2 == 0:
        return dist2(p, start)
    t = ((p[0] - start[0]) * (end[0] - start[0]) + (p[1] - start[1]) * (end[1] - start[1])) / l2
    t = max(0, min(1, t))
    dis2sag_squad = dist2(p, (start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])))
    return math.sqrt(dis2sag_squad)


def diff_xy(x1, y1, x2, y2, w):
    """Find delta x and y

    :param x1: Point1 x
    :type x1: int
    :param y1: Point1 y
    :type y1: int
    :param x2: Point2 x
    :type x2: int
    :param y2: Point2 x
    :type y2: int
    :param w: width
    :type w: int
    :return: dy, dy
    :rtype: float
    """
    if x2 - x1 != 0:
        red = math.atan(abs(y2 - y1) / abs(x2 - x1))
        dx = math.cos(red) * w
        dy = math.sin(red) * w
    else:
        dx = 0
        dy = abs(y2 - y1)/w
    return dx, dy


def length2points(p1, p2, w):
    """Find new points when width change

    :param p1: Point1
    :type p1: tuple
    :param p2: Point2
    :type p2: tuple
    :param w: width
    :type w: int
    :return: x1, y1, x2, y2
    :rtype: (int, float), (int, float), (int, float), (int, float)
    """
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    dx, dy = diff_xy(x1, y1, x2, y2, w)

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


INT_MAX = 10000


def line2rect(p1, p2, w):
    """Convert points data to rectangle

    :param p1: Point1
    :type p1: tuple
    :param p2: Point2
    :type p2: tuple
    :param w: width
    :type w: int
    :return: list of corner points
    :rtype: list[(int, float), (int, float), (int, float), (int, float)]
    """
    dx, dy = diff_xy(p1[0], p1[1], p2[0], p2[0], w)
    if p1[1] < p2[1]:
        new1_x = p1[0] - dx
        new1_y = p1[1] + dy
        new2_x = p1[0] + dx
        new2_y = p1[1] - dy

        new3_x = p2[0] + dx
        new3_y = p2[1] - dy
        new4_x = p2[0] - dx
        new4_y = p2[1] + dy
    else:
        new1_x = p1[0] - dx
        new1_y = p1[1] - dy
        new2_x = p1[0] + dx
        new2_y = p1[1] + dy

        new3_x = p2[0] + dx
        new3_y = p2[1] + dy
        new4_x = p2[0] - dx
        new4_y = p2[1] - dy

    return [(new1_x, new1_y), (new2_x, new2_y), (new3_x, new3_y), (new4_x, new4_y)]


def on_segment(p, q, r):
    """Check segmentation

    :param p: colinear
    :type p: tuple
    :param q: colinear
    :type q: tuple
    :param r: colinear
    :type r: tuple
    :return: Segmented
    :rtype: bool
    """
    if ((q[0] <= max(p[0], r[0])) &
            (q[0] >= min(p[0], r[0])) &
            (q[1] <= max(p[1], r[1])) &
            (q[1] >= min(p[1], r[1]))):
        return True

    return False


def orientation(p, q, r):
    """To find orientation of ordered triplet (p, q, r).

    :param p: colinear
    :type p: tuple
    :param q: colinear
    :type q: tuple
    :param r: colinear
    :type r: tuple
    :return: 1 Clockwise, 2 Counterclockwise
    :rtype: int
    """
    val = (((q[1] - p[1]) *
            (r[0] - q[0])) -
           ((q[0] - p[0]) *
            (r[1] - q[1])))

    if val == 0:
        return 0
    if val > 0:
        return 1  # Collinear
    else:
        return 2  # Clock or counterclock


def do_intersect(p1, q1, p2, q2):
    """Find the four orientations needed for general and special cases

    :param p1: colinear
    :type p1: tuple
    :param q1: colinear
    :type q1: tuple
    :param p2: colinear
    :type p2: tuple
    :param q2: colinear
    :type q2: tuple
    :return: True: general, False special cases
    :rtype: bool
    """
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    # p1, q1 and p2 are colinear and
    # p2 lies on segment p1q1
    if (o1 == 0) and (on_segment(p1, p2, q1)):
        return True

    # p1, q1 and p2 are colinear and
    # q2 lies on segment p1q1
    if (o2 == 0) and (on_segment(p1, q2, q1)):
        return True

    # p2, q2 and p1 are colinear and
    # p1 lies on segment p2q2
    if (o3 == 0) and (on_segment(p2, p1, q2)):
        return True

    # p2, q2 and q1 are colinear and
    # q1 lies on segment p2q2
    if (o4 == 0) and (on_segment(p2, q1, q2)):
        return True

    return False


def is_inside_polygon(points, p):
    """To check that point is in polygon or not

    :param points: polygon data
    :type points: list
    :param p: point
    :type p: tuple
    :return: true if the point p lies inside the polygon[] with n vertices
    :rtype: bool
    """
    n = len(points)

    # There must be at least 3 vertices
    # in polygon
    if n < 3:
        return False

    # Create a point for line segment
    # from p to infinite
    extreme = (INT_MAX, p[1])
    count = i = 0

    while True:
        next = (i + 1) % n

        # Check if the line segment from 'p' to
        # 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if (do_intersect(points[i],
                         points[next],
                         p, extreme)):

            # If the point 'p' is colinear with line
            # segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if orientation(points[i], p,
                           points[next]) == 0:
                return on_segment(points[i], p,
                                  points[next])

            count += 1

        i = next

        if i == 0:
            break

    # Return true if count is odd, false otherwise
    return count % 2 == 1
