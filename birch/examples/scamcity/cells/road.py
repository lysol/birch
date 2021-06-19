from birch.cells.connectable import ConnectableCell

class RoadCell(ConnectableCell):

    _default_texture = 'road_h_0'

    def __init__(self, textures, position):
        super().__init__('road', textures, position, size=[16, 16])
        self.priority = 2

    def impassable(self, cell_name):
        if cell_name == 'rail_h_0':
            return False
        return True
