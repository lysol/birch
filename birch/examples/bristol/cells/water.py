from random import randint, choice
from birch.cells.cell import Cell

class Water(Cell):

    def __init__(self, textures, position, batch=None):
        tex = randint(1,4)
        super().__init__("water", textures, position, "water_wave_%d" % tex, batch=batch)

