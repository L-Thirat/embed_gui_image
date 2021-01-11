import math


def diff_xy(x1, y1, x2, y2, l):
    red = math.atan(abs(y2 - y1) / abs(x2 - x1))
    dx = math.cos(red) * l
    dy = math.sin(red) * l
    return dx, dy


INT_MAX = 10000


def line2rect(p1, p2, w):
    print(p1, p2)
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


def on_segment(p: tuple, q: tuple, r: tuple) -> bool:
    if ((q[0] <= max(p[0], r[0])) &
            (q[0] >= min(p[0], r[0])) &
            (q[1] <= max(p[1], r[1])) &
            (q[1] >= min(p[1], r[1]))):
        return True

    return False


# To find orientation of ordered triplet (p, q, r).
# The function returns following values
# 0 --> p, q and r are colinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def orientation(p: tuple, q: tuple, r: tuple) -> int:
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
    # Find the four orientations needed for
    # general and special cases
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


# Returns true if the point p lies
# inside the polygon[] with n vertices
def is_inside_polygon(points: list, p: tuple) -> bool:
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


p1 = (2, 2.1)
polyA = [(0, 0), (2, 0), (2, 2), (0, 2)]
print(is_inside_polygon(polyA, p1))

sub_1 = (2, 2)
sub_2 = (4, 4)
w = 2

rect = line2rect(sub_1, sub_2, w)
print(rect)
print(is_inside_polygon(rect, (1.9, 2)))
print(is_inside_polygon(rect, (4, 4.1)))
