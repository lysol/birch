from birch.cells.connectable import ConnectableCell

class RoadCell(ConnectableCell):

    def __init__(self, textures, position):
        super().__init__('road', textures, position, size=[16, 16])

    def impassible(self, cell_name):
        if cell_name == 'rail_h':
            return False
        return True
