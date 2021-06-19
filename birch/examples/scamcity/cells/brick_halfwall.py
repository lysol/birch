from birch.cells.connectable import ConnectableCell

class BrickHalfWallCell(ConnectableCell):

    _default_texture = 'brick_halfwall_o_0'

    def __init__(self, textures, position):
        super().__init__('brick_halfwall', textures, position, size=[16, 16])
        self.priority = 1

    def impassable(self, cell_name):
        return True
