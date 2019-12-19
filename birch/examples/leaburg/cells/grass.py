from birch.cells.cell import Cell

class Grass(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("grass", textures, position, "grass", batch=batch)

