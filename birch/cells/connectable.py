from birch.cells.cell import Cell
from birch.util import BG_COLOR

def _lmap(f, vs):
    return list(map(f, vs))

_masks = {
    '': ['0000'],
    '_h': ['0100', '0010', '0110'],
    '_v': ['1000', '0001', '1001'],
    '_tl': ['1100'],
    '_tr': ['1010'],
    '_bl': ['0101'],
    '_br': ['0011'],
    '_x': ['1111', '1011', '0111', '1101','1110']
    }

_connection_masks = {}

for k in _masks:
    _connection_masks[k] = []
    for mask in _masks[k]:
        z = []
        for item in list(mask):
            z.append(bool(int(item)))
        _connection_masks[k].append(z)

class ConnectableCell(Cell):

    def __init__(self, name, textures, position, size=[16, 16]):
        texture_name = '%s_h' % name
        super().__init__(name, textures, position, texture_name, size=size)
        self.base_texture_name = name
        self.next_tick = 0
        self.cacheable = True

    def _connected(self, cell):
        return cell.name == self.name and (self.position[0] == cell.position[0] or \
            self.position[1] == cell.position[1])

    def _connection_match(self, comparison, connections):
        return reduce(lambda v, z: v and z,
            map(lambda item, i: comparison[i] == item, enumerate(connections)), True)

    # expects order to be [top, left, right, bottom]
    def cache_texture(self, surrounding):
        mask = [False, False, False, False]
        for cell in surrounding:
            if type(cell) != type(self) or cell == self:
                continue
            mask[0] = mask[0] or self.left == cell.left and cell.bottom == self.top
            mask[1] = mask[1] or self.right == cell.left and cell.top == self.top
            mask[2] = mask[2] or self.left == cell.right and cell.top == self.top
            mask[3] = mask[3] or self.left == cell.left and cell.top == self.bottom
        for k in _connection_masks:
            for checkmask in _connection_masks[k]:
                tex_key = '%s%s' % (self.base_texture_name, k)
                if checkmask == mask and tex_key in self.textures:
                    self.texture_name = tex_key
                    self.image = self.textures[self.texture_name]
                    return
        self.texture_name = '%s_h' % self.base_texture_name
        self.image = self.textures[self.texture_name]
