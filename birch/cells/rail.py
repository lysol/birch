from birch.cells.connectable import ConnectableCell

class RailCell(ConnectableCell):
    _masks = {
        '_h': ['01102222', '01002222', '00102222'],
        '_v': ['10012222', '00012222', '10002222'],
        '_tl': ['11002222'],
        '_tr': ['10102222'],
        '_bl': ['01012222'],
        '_br': ['00112222'],
        '_x': ['11112222', '11102222', '11012222', '10112222', '01112222']
        }

    _default_texture = 'rail_h'

    def __init__(self, textures, position):
        super().__init__('rail', textures, position, size=[16, 16])
        self.priority = 3

    def impassible(self, cell_name):
        if cell_name == 'road':
            return False
        return True
