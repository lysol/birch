from math import pi
from functools import reduce
from birch._rect import Rect

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

def join_rects(rects):
    bounds = (
        reduce(lambda a, r: r.left if r.left < a else a, rects, rects[0].left),
        reduce(lambda a, r: r.top if r.top < a else a, rects, rects[0].top),
        reduce(lambda a, r: r.right if r.right > a else a, rects, rects[0].right),
        reduce(lambda a, r: r.bottom if r.bottom > a else a, rects, rects[0].bottom),
        )
    return Rect(bounds[0], bounds[1], bounds[2] - bounds[0], bounds[3] - bounds[1])

class _Rect:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __str__(self):
        return '<Rect %d,%d to %d,%d (%d w %d h)>' % (
            self.left, self.top,
            self.right, self.bottom,
            self.w, self.h)

    @property
    def bounds(self):
        return (self.x, self.y, self.w, self.h)

    @property
    def center(self):
        return self.x + int(self.width / 2), self.y + int(self.height / 2)

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

    def colliderect(self, rect):
        x = rect.x
        y = rect.y
        w = rect.w
        h = rect.h
        l = x
        t = y
        b = y + h - 1
        r = x + w - 1
        return not (
            r < self.left or \
            l > self.right - 1 or \
            b < self.top or \
            t > self.bottom - 1
            )
pi2 = pi * 2

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
FG_COLOR = BLACK
BG_COLOR = WHITE
