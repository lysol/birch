from pygame import Rect
from cells import *

class Cell:

    def __init__(self, name, textures, position, texture_name=None):
        self.name = name
        if texture_name is None:
            texture_name = name
        self.texture_name = texture_name
        self.textures = textures
        self.position = position
        self.next_tick = 0

    def draw(self, camera, screen):
        coords = self.get_rect(camera)
        return screen.blit(self.textures[self.texture_name], coords)

    def get_rect(self, camera):
        return Rect(
            self.position[0] * 32 + camera[0],
            self.position[1] * 32 + camera[1],
            32,
            32
        )

    def tick(self, ticks, engine):
        return False
