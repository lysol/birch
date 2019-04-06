from uuid import uuid4
from pyglet import sprite
from birch.util import negate, BG_COLOR, Rect
from birch.cells import *

class Cell(sprite.Sprite):

    def __init__(self, name, textures, position, texture_name, batch=None,
            size=None, priority=0):
        super().__init__(textures[texture_name], position[0], position[1], batch=batch)
        self.name = name
        self.texture_name = texture_name
        self.textures = textures
        self.position = position
        self.next_update = -1
        self._impassible = False
        self.id = uuid4()
        self.priority = priority
        #self.size = size if size is not None else [self.sprite.width, self.sprite.height]
        self.scale = 2.0
        self.set_dimensions()

    def __setattr__(self, attrname, value):
        supper = super()
        supper.__setattr__(attrname, value)
        if hasattr(self, '_dimensions') and attrname in self._dimensions:
            self.set_dimensions()

    def set_dimensions(self):
        topper = super()
        self._dimensions = {
            'left': self.position[0],
            'right': self.position[0] + topper.width,
            'bottom': self.position[1] + topper.height,
            'top': self.position[1],
            'width': topper.width,
            'height': topper.height,
            'topleft': (topper.x, topper.y),
            'topright': (topper.x + topper.width, topper.y),
            'bottomleft': (topper.x, topper.y + topper.height),
            'bottomright': (topper.x + topper.width, topper.y + topper.height),
            'rect': Rect(topper.x, topper.y, topper.width, topper.height)
        }

    def __str__(self):
        return '%s: %s' % (self.__class__, str(self.bounds))

    def __repr__(self):
        return self.__str__()

    def _shift(self, delta):
        return self.position[0] + delta[0], self.position[1] + delta[1]

    @property
    def width(self):
        return self._dimensions['width']

    @property
    def height(self):
        return self._dimensions['height']

    @property
    def w(self):
        return self.width

    @property
    def h(self):
        return self.height

    @property
    def left(self):
        return self._dimensions['left']

    @property
    def top(self):
        return self._dimensions['top']

    @property
    def right(self):
        return self._dimensions['right']

    @property
    def bottom(self):
        return self._dimensions['bottom']

    @property
    def topleft(self):
        return self._dimensions['topleft']

    @property
    def topright(self):
        return self._dimensions['topright']

    @property
    def bottomleft(self):
        return self._dimensions['bottomleft']

    @property
    def bottomright(self):
        return self._dimensions['bottomright']

    @property
    def rect(self):
        return self._dimensions['rect']

    @property
    def bounds(self):
        return self._dimensions['rect'].bounds

    def collidepoint(self, x, y):
        return x >= self.left and x < self.right and \
                y >= self.top and y < self.bottom

    def intersects(self, x, y=None, w=None, h=None):
        if issubclass(type(x), Cell):
            sprite = x
            x = sprite.x
            y = sprite.y
            w = sprite.w
            h = sprite.h
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

    def viewed_position(self, camera):
        return self._shift(negate(camera))

    def update(self, ticks, engine):
        return False

    def impassible(self, cell):
        return self._impassible
