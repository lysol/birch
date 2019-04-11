from birch.cells.cell import Cell
from birch.util import BG_COLOR
from random import shuffle

class ConnectableCell(Cell):
    _masks = {
        '': ['00000000'],
        '_h': ['01100000'],
        '_v': ['10010000'],
        '_tl': ['11000000'],
        '_tr': ['10100000'],
        '_bl': ['01010000'],
        '_br': ['00110000'],
        '_x': ['11110000'],
        '_o': ['00000000'],
        '_i_tl': ['10011101'],
        '_i_tr': ['11001110'],
        '_i_bl': ['00111011'],
        '_i_br': ['01100111'],
        '_u_tl': ['01100010'],
        '_u_tr': ['00110001'],
        '_u_bl': ['01100010'],
        '_u_br': ['10011000'],
        '_f': ['11111111'],
        '_hl': ['01000000'],
        '_hr': ['00100000'],
        '_vt': ['10000000'],
        '_vb': ['00100000'],
        '_vr': ['11100110'],
        '_vl': ['10111001'],
        '_hb': ['01110011'],
        '_ht': ['11011100'],
        '_ltee': ['11100000'],
        '_ttee': ['01110000'],
        '_rtee': ['10110000'],
        '_btee': ['11010000']
        }

    _connection_mask_map = {}
    _connection_masks = {}

    def __init__(self, name, textures, position, size=[16, 16]):
        for k in self._masks:
            self._connection_masks[k] = []
            for mask in self._masks[k]:
                z = []
                for item in list(mask):
                    z.append(int(item))
                self._connection_masks[k].append(z)

        texture_name = '%s_h' % name
        super().__init__(name, textures, position, texture_name, size=size)
        self.base_texture_name = name
        self.next_tick = 0

    def mask_matched(self, mask1, mask2):
        for i, item in enumerate(mask2):
            if item == 2:
                # wildcard in the second
                mask1[i] = 2
        res = mask1 == mask2
        return res

    # expects order to be [top, left, right, bottom]
    def cache_texture(self, surrounding):
        # create a list of suffixes, including none, to check for textures
        # with some variation
        suffixes = ['_0', '_1']
        shuffle(suffixes)
        items = ['']
        items.extend(suffixes)
        mask = [0, 0, 0, 0, 0, 0, 0, 0]
        for cell in surrounding:
            if type(cell) != type(self) or cell == self:
                continue
            mask[0] = mask[0] or self.left == cell.left and cell.bottom == self.top
            mask[1] = mask[1] or self.right == cell.left and cell.top == self.top
            mask[2] = mask[2] or self.left == cell.right and cell.top == self.top
            mask[3] = mask[3] or self.left == cell.left and cell.top == self.bottom
            mask[4] = mask[4] or self.left == cell.right and cell.bottom == self.top
            mask[5] = mask[5] or self.right == cell.left and cell.bottom == self.top
            mask[6] = mask[6] or self.left == cell.right and cell.top == self.bottom
            mask[7] = mask[7] or self.right == cell.left and cell.top == self.bottom
            mask = list(map(lambda item: int(item), mask))

        """
        ok here's how this works.

        first, we enumerate the keys of self._connection_masks. We are looking for
        a case where the True/False settings of this match to what we deduced above.
        If we find 'k' that matches, we also check to see if there is an included
        mapping of other _suffixes to k. In this manner there can be a default
        texture for many kinds of connections between cells.

        Otherwise, if there's no mapping the mapping is deduced based on the original
        k value.

        After this, we check for two types of textures: ones that end in k/sfx, and then
        those that end in that plus _0 or _1. This way there can be some variation in
        textures.
        """

        for k in self._connection_masks:
            for checkmask in self._connection_masks[k]:
                mapped = [k]
                # look for other suffixes that should be checked instead of this
                # name.
                if k in self._connection_mask_map:
                    mapped = self._connection_mask_map[k]
                for sfx in mapped:
                    tex_key = '%s%s' % (self.base_texture_name, sfx)
                    # cycle through our prebuilt list of suffixes and see if a tex exists
                    for item in items:
                        retex_key = '%s%s' % (tex_key, item)
                        if self.mask_matched(mask, checkmask) and retex_key in self.textures:
                            self.texture_name = retex_key
                            self.image = self.textures[self.texture_name]
                            return
        self.texture_name = '%s_h' % self.base_texture_name
        self.image = self.textures[self.texture_name]
