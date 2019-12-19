from birch.cells.cell import Cell

class SmallSpikes(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("small_spikes", textures, position, "small_spikes", batch=batch)

