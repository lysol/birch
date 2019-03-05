from pygame import Rect
from cells import *
from uuid import uuid4
from util import negate

class Cell:

    def __init__(self, name, textures, position, texture_name=None,
            size=None):
        self.name = name
        if texture_name is None:
            texture_name = name
        self.texture_name = texture_name
        self.textures = textures
        self.position = position
        self.next_tick = 0
        self.id = uuid4()
        # use the texture to get the size if it is None
        if size is not None:
            self.size = size
        else:
            self.size = self.textures[self.texture_name].get_size()

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def draw(self, camera, screen):
        coords = self.get_rect(camera)
        return screen.blit(self.textures[self.texture_name], coords)

    @property
    def topleft(self):
        return self.rect.topleft

    @property
    def topright(self):
        return self.rect.topright

    @property
    def bottomleft(self):
        return self.rect.bottomleft

    @property
    def bottomright(self):
        return self.rect.bottomright

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @property
    def rect(self):
        r = Rect(
            self.position[0],
            self.position[1],
            self.size[0],
            self.size[1]
            )
        return r

    def get_rect(self, camera):
        rect = self.rect.move(*negate(camera))
        return rect

    def tick(self, ticks, engine):
        return False
