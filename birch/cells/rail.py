from birch.cells.connectable import ConnectableCell

class RailCell(ConnectableCell):

    def __init__(self, textures, position):
        super().__init__('rail', textures, position, size=[32, 32])
        self.priority = 3

    def impassible(self, cell_name):
        if cell_name == 'road_h':
            return False
        return True
