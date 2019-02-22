from cells.cell import Cell
from random import randint

class RCell(Cell):

    def __init__(self, textures, position):
        super().__init__("r", textures, position)


class CCell(Cell):

    def __init__(self, textures, position):
        super().__init__("c", textures, position)


class ICell(Cell):

    def __init__(self, textures, position):
        super().__init__("i", textures, position)

