from uuid import uuid4
import pygame
from pygame import Rect, draw, Surface, SRCALPHA, HWSURFACE
from birch.util import negate, BG_COLOR
from birch.cells import *

class Cell:

    def __init__(self, name, textures, position, texture_name,
            size=None, priority=0):
        self.name = name
        self.sprite = textures.get_sprite(texture_name, *position)
        self.texture_name = texture_name
        self.textures = textures
        self.position = position
        self.next_tick = 0
        self._impassible = False
        self.id = uuid4()
        self.priority = priority
        self.size = size if size is not None else [self.sprite.width, self.sprite.height]
        self.update_rect()

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

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
        return self._rect

    def update_rect(self):
        self._rect = Rect(
            self.position[0],
            self.position[1],
            self.size[0],
            self.size[1]
            )
        return self._rect

    def get_rect(self, camera):
        rect = self.rect.move(*negate(camera))
        return rect

    def tick(self, ticks, engine):
        return False

    def impassible(self, cell):
        return self._impassible
