from cells.cell import Cell
from random import randint

class RCell(Cell):

    def __init__(self, textures, position):
        super().__init__("r", textures, position)
        self.ticks = 0

    def tick(self, ticks, engine):
        self.ticks = ticks

class CCell(Cell):

    def __init__(self, textures, position):
        super().__init__("c", textures, position)
        self.ticks = 0

    def tick(self, ticks, engine):
        self.ticks = ticks

class ICell(Cell):

    def __init__(self, textures, position):
        super().__init__("i", textures, position)
        self.ticks = 0

    def tick(self, ticks, engine):
        self.ticks = ticks

