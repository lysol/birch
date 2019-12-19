from birch.cells.cell import Cell

class Spikes(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("spikes", textures, position, "spikes", batch=batch)

