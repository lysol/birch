from birch.cells.connectable import ConnectableCell

class RoadCell(ConnectableCell):

    def __init__(self, textures, position):
        super().__init__('road', textures, position, size=[16, 16])

