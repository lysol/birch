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


class Rect:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def topleft(self):
        return (self.x, self.y)

    @property
    def topright(self):
        return (self.x + self.w, self.y)

    @property
    def bottomleft(self):
        return (self.x, self.y + self.h)

    @property
    def bottomright(self):
        return (self.x + self.w, self.y + self.h)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    def inflate(self, w, h):
        return Rect(self.x - w / 2, self.y - w / 2, self.w + w, self.h + h)

    @property
    def width(self):
        return self.w

    @property
    def height(self):
        return self.h

    def collidepoint(self, xy):
        x, y = xy
        return x >= self.x and x < self.x + self.w and \
            y >= self.y and y < self.y + self.h

pi2 = pi * 2

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
FG_COLOR = BLACK
BG_COLOR = WHITE
