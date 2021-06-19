from birch.cells.connectable import ConnectableCell

class BrickWallCell(ConnectableCell):

    _default_texture = 'brick_wall_o_0'

    def __init__(self, textures, position):
        super().__init__('brick_wall', textures, position, size=[16, 16])
        self.priority = 1

    def impassable(self, cell_name):
        return True
