from math import pi

def clamp(i, mini, maxi):
    return min(max(i, mini), maxi)

def negate(stuff):
    return tuple(map(lambda x: -x, stuff))

def fix_origin(vertexes, height):
    outvx = []
    for o in range(0, len(vertexes), 2):
        outvx.append(vertexes[o])
        outvx.append(height - vertexes[o + 1])
    return tuple(outvx)

pi2 = pi * 2

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
FG_COLOR = BLACK
BG_COLOR = WHITE
