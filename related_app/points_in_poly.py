from shapely.geometry import Point, Polygon
# import geopandas as gpd
# from geopandas import GeoSeries
import shapely.speedups
import numpy as np

shapely.speedups.enable()

# cnt = [[[441 139]]
#
#  [[442 138]]
#
#  [[443 138]]
#
#  [[444 139]]
#
#  [[444 142]]
#
#  [[440 146]]
#
#  [[439 146]]
#
#  [[435 150]]
#
#  [[434 150]]
#
#  [[433 151]]
#
#  [[431 149]]
#
#  [[432 148]]
#
#  [[432 147]]
#
#  [[440 139]]]
ary = np.array([[[1, 1]], [[2, 3]]])
x = [item[0][0] for item in ary]
y = [item[0][1] for item in ary]
# print(ary)
# print(ary.flatten())
# x = np.linspace(0,5,10)
# y = np.linspace(0,5,10)
# x, y = np.meshgrid(x, y)
# x, y = x.flatten(), y.flatten()
# print(x, y)
p1 = Point(2, 3)
# s = GeoSeries(map(Point, zip(x, y)))
polyA = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
# df = s.within(polyA)
# print(df)
# err_p_idx = (list(df[df==False].index))
# print()
# print(s)
# print(list(s.iloc[err_p_idx])[0].x)
# print(list(s.iloc[err_p_idx])[0].y)
# print(s.iloc[err_p_idx])
# print([np.array(err_p) for err_p in s.iloc[err_p_idx]])

# -------------
polyB = Polygon([(0.1, 0.1), (1.9, 0.0), (1.9, 1.9), (0.1, 1.9)])
polyC = Polygon([(0.1, 0.1), (1.9, 0.0), (2, 2.1), (0.1, 1.9)])
print(polyA.intersects(polyB))
print(polyB.within(polyA))
print(polyC.within(polyA))
print(polyA.within(polyA))
