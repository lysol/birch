from uuid import uuid4
from pyglet import sprite
import pygame
from pygame import Rect, draw, Surface, SRCALPHA, HWSURFACE
from birch.util import negate, BG_COLOR
from birch.cells import *

class Cell(sprite.Sprite):

    def __init__(self, name, textures, position, texture_name, batch=None,
            size=None, priority=0):
        super().__init__(textures[texture_name], position[0], position[1], batch=batch)
        self.name = name
        self.texture_name = texture_name
        self.textures = textures
        self.real_position = position
        self.position = position
        self.next_tick = 0
        self._impassible = False
        self.id = uuid4()
        self.priority = priority
        #self.size = size if size is not None else [self.sprite.width, self.sprite.height]
        self.update_rect()
        self.scale = 2.0

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
    def rect(self):
        return self._rect

    def update_rect(self):
        self._rect = Rect(
            self.real_position[0],
            self.real_position[1],
            self.width,
            self.height
            )
        return self._rect

    def get_rect(self, camera):
        rect = self.rect.move(*negate(camera))
        return rect

    def set_pos(self, camera):
        self.x = self.real_position[0] - camera[0]
        self.y = self.real_position[1] - camera[1]

    def update(self, dt):
        return False

    def impassible(self, cell):
        return self._impassible
