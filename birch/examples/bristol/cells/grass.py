from random import randint, choice
from birch.cells.cell import Cell

class ShortGrass(Cell):

    def __init__(self, textures, position, batch=None):
        tex = randint(1,3)
        super().__init__("short_grass", textures, position, "short_grass_breeze_%d" % tex, batch=batch)

