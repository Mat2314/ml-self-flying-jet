from collections import namedtuple
from enum import IntEnum

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
RADAR_SIZE = 5
SPEED = 40

RectObjectCoordinates = namedtuple('RectObjectCoordinates','left,right,top,bottom')
PlaneData = namedtuple('PlaneData', 'left, top, width, height')

class RadarSquares(IntEnum):
    TOP_LEFT = 1
    TOP = 2
    TOP_RIGHT = 3
    TOP_RIGHT_FAR = 4
    LEFT = 5
    RIGHT = 6
    RIGHT_FAR = 7
    BOTTOM_LEFT = 8
    BOTTOM = 9
    BOTTOM_RIGHT = 10
    BOTTOM_RIGHT_FAR = 11
