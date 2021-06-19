from birch.cells.connectable import ConnectableCell

class WaterCell(ConnectableCell):

    _default_texture = 'water_o_0'

    def __init__(self, textures, position):
        super().__init__('water', textures, position, size=[16, 16])
        self.priority = 1

    def impassable(self, cell_name):
        return True
