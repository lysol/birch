from math import pi

def clamp(i, mini, maxi):
    return min(max(i, mini), maxi)

def negate(stuff):
    return tuple(map(lambda x: -x, stuff))

pi2 = pi * 2

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
FG_COLOR = BLACK
BG_COLOR = WHITE
