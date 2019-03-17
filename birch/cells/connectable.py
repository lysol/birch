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
            same_x = self.rect.topleft[0] == cell.rect.topleft[0]
            same_y = self.rect.topleft[1] == cell.rect.topleft[1]
            x_offset = self.rect.topleft[0] - cell.rect.topleft[0]
            y_offset = self.rect.topleft[1] - cell.rect.topleft[1]
            mask[0] = mask[0] or same_x and y_offset == -self.height
            mask[1] = mask[1] or same_y and x_offset == -self.width
            mask[2] = mask[2] or same_y and x_offset == self.width
            mask[3] = mask[3] or same_x and y_offset == self.height
        for k in _connection_masks:
            for checkmask in _connection_masks[k]:
                tex_key = '%s%s' % (self.base_texture_name, k)
                if checkmask == mask and tex_key in self.textures:
                    self.texture_name = tex_key
                    self.dirty_texture = True
                    return
        self.texture_name = '%s_h' % self.base_texture_name
        self.dirty_texture = True
