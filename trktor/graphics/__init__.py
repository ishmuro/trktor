from collections import namedtuple

Point2D = namedtuple("Point2D", ["x", "y"], defaults=[0, 0])
Line2D = namedtuple("Line2D", ["xs", "ys", "xe", "ye"], defaults=[0, 0, 0, 0])
RGBAColor = namedtuple("RGBAColor", ["r", "g", "b", "a"], defaults=[0, 0, 0, 0])
MarginSet = namedtuple("MarginSet", ["left", "top", "right", "bottom"], defaults=[0, 0, 0, 0])
Dim2D = namedtuple("Dim2D", ["width", "height"], defaults=[0, 0])

TRANSPARENT_WHITE: RGBAColor = RGBAColor(255, 255, 255, 0)
TRANSPARENT_BLACK: RGBAColor = RGBAColor(0, 0, 0, 0)

ORIGIN: Point2D = Point2D(0, 0)

NO_MARGINS: MarginSet = MarginSet(0, 0, 0, 0)