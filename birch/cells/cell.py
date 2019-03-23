from uuid import uuid4
from pyglet import sprite
from birch.util import negate, BG_COLOR
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
        return str(self.__class__) + ": " + str(self.__dict__)

    def _shift(self, delta):
        return self.position[0] + delta[0], self.position[1] + delta[1]

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

    def intersects(self, x, y, w=None, h=None):
        if w is None or h is None:
            points = [(x, y)]
        else:
            r = x + w - 1
            b = y + h - 1
            points = ((x, y),
                (r, y),
                (r, b),
                (x, b))
        for a, b in points:
            if a >= self.x and b >= self.y and \
                a < self.x + self.width and \
                b < self.y + self.height:
                return True
        return False

    def viewed_position(self, camera):
        return self._shift(negate(camera))

    def update(self, dt):
        return False

    def impassible(self, cell):
        return self._impassible
