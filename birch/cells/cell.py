from uuid import uuid4
import pygame
from pygame import Rect, draw, Surface, SRCALPHA, HWSURFACE
from birch.util import negate, BG_COLOR
from birch.cells import *

class Cell:

    def __init__(self, name, textures, position, texture_name,
            size=None, priority=0):
        self.name = name
        self.texture_name = texture_name
        self.textures = textures
        self.position = position
        self.next_tick = 0
        self._impassible = False
        self.id = uuid4()
        self.priority = priority
        # use the texture to get the size if it is None
        texture_size = self.textures[self.texture_name].get_size()
        if size is not None:
            self.size = size
        else:
            self.size = texture_size
        self._rect = Rect(
            self.position[0],
            self.position[1],
            self.size[0],
            self.size[1]
            )
        self._last_texture = None
        self._texture = None
        self.dirty_texture = False
        self._init_texture()

    def _init_texture(self):
        if self._texture is None or self._last_texture is None or \
            self._last_texture != self.texture_name:
            texture_size = self.textures[self.texture_name].get_size()
            if texture_size[0] < self.size[0] or texture_size[1] < self.size[1]:
                # need to tile
                try:
                    self._texture = Surface(self.size, flags=(SRCALPHA | HWSURFACE))
                except pygame.error as e:
                    raise e
                plot = [0, 0]
                while plot[0] < self.size[0]:
                    while plot[1] < self.size[1]:
                        self._texture.blit(self.textures[self.texture_name],
                            Rect(plot[0], plot[1], texture_size[0], texture_size[1]))
                        plot[1] += texture_size[1]
                    plot[0] += texture_size[0]
                    plot[1] = 0
            else:
                self._texture = self.textures[self.texture_name]
            self._last_texture = self.texture_name
            self.dirty_texture = False

    @property
    def texture(self):
        if self.dirty_texture:
            self._init_texture()
        return self._texture

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def draw(self, camera, screen):
        coords = self.get_rect(camera)
        return screen.blit(self.texture, coords)

    def draw_box(self, camera, screen, color):
        coords = self.get_rect(camera)
        return draw.rect(screen, color, coords, 1)

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
