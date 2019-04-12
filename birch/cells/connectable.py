from birch.cells.cell import Cell
from birch.util import BG_COLOR
from random import shuffle

class ConnectableCell(Cell):
    _masks = {
        '': '00000000',
        '_h': '01102222',
        '_v': '10012222',
        '_tl': '00112220',
        '_tr': '01012202',
        '_bl': '10102022',
        '_br': '11000222',
        '_x': '11110000',
        '_o': '00000000',
        '_i_tl': '11111110',
        '_i_tr': '11111101',
        '_i_bl': '11111011',
        '_i_br': '11110111',
        '_u_tl': '00112221',
        '_u_tr': '01012212',
        '_u_br': '11001222',
        '_u_bl': '10102122',
        '_f': '11111111',
        '_hl': '00102222',
        '_hr': '01002222',
        '_vt': '00012222',
        '_vb': '10002222',
        '_vl': '10112121',
        '_vr': '11011212',
        '_hb': '11101122',
        '_ht': '01112211',
        '_ltee': '10112020',
        '_ttee': '01112200',
        '_rtee': '11010202',
        '_btee': '11100022',
        '_yt': '11110011',
        '_yb': '11111100',
        '_yl': '11110101',
        '_yr': '11111010',
        '_ytlt': '10112021',
        '_ytll': '01112201',
        '_ytrt': '11010212',
        '_ytrr': '01112210',
        '_ybrb': '11011202',
        '_ybrr': '11101022',
        '_yblb': '10112120',
        '_ybll': '11100122',
        '_ydr': '11110110',
        '_ydl': '11111001',
        '_ytlx': '11110001',
        '_ytrx': '11110010',
        '_yblx': '11110100',
        '_ybrx': '11111000'
        }

    _default_texture = ''
    _connection_mask_map = {}
    _connection_masks = {}

    def __init__(self, name, textures, position, size=[16, 16]):
        if len(self._connection_masks) == 0:
            for k in self._masks:
                self._connection_masks[k] = []
                mask = self._masks[k]
                z = []
                for item in list(mask):
                    z.append(int(item))
                self._connection_masks[k].append(z)

        texture_name = self._default_texture
        super().__init__(name, textures, position, texture_name, size=size)
        self.base_texture_name = name
        self.next_tick = 0

    # expects order to be [top, left, right, bottom]
    def cache_texture(self, surrounding):
        # create a list of suffixes, including none, to check for textures
        # with some variation
        suffixes = ['_0', '_1']
        shuffle(suffixes)
        items = ['']
        items.extend(suffixes)
        zoro = [0, 0, 0, 0, 0, 0, 0, 0]
        mask = list(zoro)
        for cell in surrounding:
            if type(cell) != type(self) or cell == self:
                continue
            tb = cell.top == self.bottom
            bb = cell.bottom == self.bottom
            bt = cell.bottom == self.top
            ll = self.left == cell.left
            lr = self.left == cell.right
            rl = self.right == cell.left
            mask[0] = mask[0] or ll and tb
            mask[1] = mask[1] or lr and bb
            mask[2] = mask[2] or rl and bb
            mask[3] = mask[3] or ll and bt
            mask[4] = mask[4] or lr and tb
            mask[5] = mask[5] or rl and tb
            mask[6] = mask[6] or lr and bt
            mask[7] = mask[7] or rl and bt
            mask = list(map(lambda item: int(item), mask))
        if mask == zoro:
            return

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
                matched = True
                for (i, z) in enumerate(mask):
                    if checkmask[i] == 2:
                        continue
                    if z != checkmask[i]:
                        matched = False
                        break
                if not matched:
                    continue
                # look for other suffixes that should be checked instead of this
                # name.
                if k in self._connection_mask_map:
                    mapped = self._connection_mask_map[k]
                for sfx in mapped:
                    tex_key = '%s%s' % (self.base_texture_name, sfx)
                    # cycle through our prebuilt list of suffixes and see if a tex exists
                    for item in items:
                        retex_key = '%s%s' % (tex_key, item)
                        if retex_key in self.textures:
                            self.texture_name = retex_key
                            self.image = self.textures[self.texture_name]
                            return
        self.texture_name = self._default_texture
        self.image = self.textures[self.texture_name]
