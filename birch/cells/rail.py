from cells.connectable import ConnectableCell

class RailCell(ConnectableCell):

    def __init__(self, textures, position):
        super().__init__('rail', textures, position, size=[16, 16])

