from cells.cell import Cell
from random import randint

class Uranium(Cell):

    def __init__(self, textures, position):
        super().__init__("uranium", textures, position)
        self.decay_left = randint(200, 300)
        self.ticks = 0

    def tick(self, ticks):
        if self.decay_left > 0:
            self.decay_left -= ticks - self.ticks
        if self.decay_left <= 0:
            self.texture_name = "dirt"
        self.ticks = ticks
