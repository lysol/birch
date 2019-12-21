from birch.cells.cell import Cell

class Flower(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("flower", textures, position, "flower", batch=batch)

class Flower2(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("flower2", textures, position, "flower2", batch=batch)
