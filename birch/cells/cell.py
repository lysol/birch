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
        self.next_tick = 0
        self._impassible = False
        self.id = uuid4()
        self.priority = priority
        #self.size = size if size is not None else [self.sprite.width, self.sprite.height]
        self.scale = 2.0

    def __str__(self):
        return '%s: %s' % (self.__class__, str(self.bounds))

    def __repr__(self):
        return self.__str__()

    def _shift(self, delta):
        return self.position[0] + delta[0], self.position[1] + delta[1]

    @property
    def w(self):
        return self.width

    @property
    def h(self):
        return self.height

    @property
    def left(self):
        return self.position[0]

    @property
    def top(self):
        return self.position[1]

    @property
    def right(self):
        return self.position[0] + self.width

    @property
    def bottom(self):
        return self.position[1] + self.height

    @property
    def topleft(self):
        return self.position

    @property
    def topright(self):
        return self._shift((self.width, 0))

    @property
    def bottomleft(self):
        return self._shift((0, self.height))

    @property
    def bottomright(self):
        return self._shift((self.width, self.height))

    @property
    def rect(self):
        return Rect(self.x, self.y, self.w, self.h)

    @property
    def bounds(self):
        return self.rect.bounds

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

    def update(self, dt):
        return False

    def impassible(self, cell):
        return self._impassible
