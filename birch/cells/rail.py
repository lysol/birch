from birch.cells.connectable import ConnectableCell

class RailCell(ConnectableCell):
    _default_texture = 'rail_h_0'

    def __init__(self, textures, position):
        super().__init__('rail', textures, position, size=[16, 16])
        self.priority = 3

    def impassible(self, cell_name):
        if cell_name == 'road':
            return False
        return True
