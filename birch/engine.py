from os import unlink
from random import choice, randint, random
from math import sin, pi, hypot
from collections import deque
from uuid import uuid4
from noise import pnoise2, snoise2
from pyglet.gl import *
from pyglet import resource
from pyglet.sprite import Sprite
import pyglet
from PIL import Image, ImageDraw
from birch.cells.rci import RCell, CCell, ICell
from birch.cells.cell import Cell
from birch.cells.connectable import ConnectableCell
from birch.cells.road import RoadCell
from birch.cells.rail import RailCell
from birch.cells.uranium import Uranium
from birch.cells.tree import PineTree, BirchTree
from birch.util import clamp, pi2, Rect
from birch.world import World

class Engine:

    freqs = {
        "r": 10000,
        "c": 8000,
        "i": 5000
        }

    freq_mod = 0.1

    demand_offset = {
        "r": 1500,
        "c": 5000,
        "i": 850
        }

    ratios = {
        "r": {
            "r": 3000,
            "c": 1,
            "i": 1000
        },
        "c": {
            "r": 2,
            "c": 0,
            "i": 1
        },
        "i": {
            "r": 5,
            "c": 1,
            "i": 0
        }
    }

    overall_factor = 1.0

    rci_interval = 20

    cell_minimum = 16
    insert_chunk = 15

    def __init__(self, state, textures):
        self.state = state
        self.ticks = 0
        self.textures = textures
        self._next_rci = 0
        self._demand_calc()
        self.world = World()
        self.deferred_inserts = deque([])
        self.randoms = []

    def in_range(self, camera, pos):
        return pos[0] > camera[0] - 1000 or \
            pos[0] < camera[0] + 1000 or \
            pos[1] < camera[1] - 1000 or \
            pos[1] < camera[1] + 1000

    def tick(self, checkrect=None):
        damage = False
        self.ticks += self.state["speed"]
        changed = []
        cr = checkrect.inflate(checkrect.width, checkrect.height)
        in_range_cells = self.world.get(*cr.topleft, cr.width, cr.height)
        self.gen_random()
        if self._next_rci <= self.ticks:
            self._demand_calc()
            self._rci()
            self._next_rci = self.ticks + self.rci_interval
        if len(self.deferred_inserts) > 0:
            inserted = self.do_insert()
            if checkrect is not None:
                for item in inserted:
                    if checkrect.colliderect(item.rect):
                        changed.append(item)
            else:
                changed.extend(inserted)
        return changed

    def _demand_calc(self):
        self.state["demand"] = {}
        for ckey in self.freqs:
            # use a sine wave to express demand waves
            curticks = round(self.freq_mod * self.ticks) + self.demand_offset[ckey]
            ratio = curticks % self.freqs[ckey] / float(self.freqs[ckey])
            point = sin(ratio * pi2)
            self.state["demand"][ckey] = \
                (point + 1.0) / 2.0

    def _rci(self):
        rci = ['r','c','i']
        workcells = {k: [] for k in rci}
        self.state["population"] = 0
        for cell in self.state["cells"]:
            if type(cell) is RCell:
                workcells['r'].append(cell)
            elif type(cell) is CCell:
                workcells['c'].append(cell)
            elif type(cell) is ICell:
                workcells['i'].append(cell)
            if hasattr(cell, 'population'):
                self.state["population"] += cell.population
        for ct in rci:
            for cell in workcells[ct]:
                if type(cell) is RCell:
                    ckey = 'r'
                elif type(cell) is CCell:
                    ckey = 'c'
                elif type(cell) is ICell:
                    ckey = 'i'
                if randint(0, 100) < 25 * abs(cell.demand):
                    cell.populate()
                    cell.level_check()
                neighbors = self.get_surrounding(cell)
                counts = {
                    "r": 0,
                    "c": 0,
                    "i": 0
                    }
                populations = {
                    "r": 0,
                    "c": 0,
                    "i": 0
                    }
                demand = 0
                for n in neighbors:
                    if n.id == cell.id:
                        pass
                    if type(n) is RCell:
                        counts['r'] += 1
                        populations['r'] += n.population
                    elif type(n) is CCell:
                        counts['c'] += 1
                        populations['c'] += n.population
                    elif type(n) is ICell:
                        counts['i'] += 1
                        populations['i'] += n.population
                for ct in counts:
                    demand += counts[ct] * \
                        self.ratios[cell.base_texture_name][ct] * \
                        clamp(populations[ct] / 100, -1, 1)
                demand = clamp(demand + (self.state["demand"][ckey] - 0.5) * self.overall_factor, -1, 1)
                cell.demand = demand

    def get_surrounding(self, cell):
        bounds = cell.rect.inflate(cell.width * 2, cell.height * 2).bounds
        return self.world.get(*bounds)

    def get_cell(self, x, y, w, h):
        return self.world.get(x, y, w, h)

    def do_insert(self):
        cells = []
        for z in range(self.insert_chunk):
            if len(self.deferred_inserts) == 0:
                break
            cell = self.deferred_inserts.popleft()
            cells.append(cell)
        if len(cells) > 0:
            self.state['cells'].extend(cells)
            for cell in cells:
                self.world.insert(cell, *cell.position)
                self.texture_check(cell)
        return cells

    def set_cell(self, cell, alias=True, grow=True, defer=False):
        if alias:
            apos = self.alias_pos(cell.left, cell.top)
            cell.position = apos[0], apos[1]
        if defer:
            self.deferred_inserts.append(cell)
        else:
            self.state['cells'].append(cell)
            self.world.insert(cell, *cell.position)
            self.texture_check(cell)

    def texture_check(self, cell):
        if issubclass(type(cell), ConnectableCell):
            newbounds = cell.rect.inflate(cell.width * 2, cell.height * 2).bounds
            surrounding = self.world.get(*newbounds)
            for other in surrounding:
                if type(other) == type(cell):
                    other.cache_texture(self.get_surrounding(other))

    def del_cell(self, cell):
        self.world.delete(cell, *cell.position)
        if cell in self.state['cells']:
            self.state['cells'].remove(cell)

    def alias_pos(self, x, y, size=16):
        return [
            x - x % size,
            y - y % size
            ]

    def use_tool(self, name, x, y, tool_size=32):
        # assuming x, y is already aliased.
        if name is None:
            return
        tooltex = self.textures[name]
        intersected = self.get_cell(x, y,
            tool_size, tool_size)
        cells = []
        for cell in intersected:
            if cell.impassible(name):
                cells.append(cell)

        new_cell = None
        if name == "bulldoze":
            for cell in cells:
                self.del_cell(cell)
        elif len(cells) == 0:
            for cell in intersected:
                if not cell.impassible:
                    self.del_cell(cell)
            if name == "r_0_0":
                new_cell = RCell(self.textures, (x, y))
            elif name == "c_0_0":
                new_cell = CCell(self.textures, (x, y))
            elif name == "i_0_0":
                new_cell = ICell(self.textures, (x, y))
            elif name == "road_h":
                new_cell = RoadCell(self.textures, (x, y))
            elif name == "rail_h":
                new_cell = RailCell(self.textures, (x, y))
        if new_cell is not None:
            self.set_cell(new_cell, alias=False)

    def get_batches(self, x, y, w, h):
        r = Rect(x, y, w, h).inflate(w, h)
        return self.world.get_batches(*r.topleft, r.width, r.height)

    def gen_random(self):
        maxd = self.world.chunk_size * self.world.chunk_size
        if len(self.randoms) < maxd:
            for z in range(2048):
                self.randoms.append(random())

    def rands(self):
        if len(self.randoms) == 0:
            self.gen_random()
        x = self.randoms.pop()
        return x

    def create_background(self, ix, iy):
        dims = [int(self.world.chunk_size / 2)] * 2
        img = Image.new('RGBA', dims)
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, dims[0], dims[1]), fill=(255, 255, 255, 0))
        pixels = img.load()
        # draw dirt stuff
        octaves = 1
        freq = 32.0
        dirts = 0
        size = 8
        for x in range(0, dims[0], size):
            for y in range(0, dims[1], size):
                ox, oy = ix + x, iy + y
                noised = snoise2(ox / freq * 2, oy / freq * 2) * 0.2 + 0.5
                thresh = self.rands()
                if noised > thresh: #noised % 2 == 0:
                    dirts  = dirts + 1
                    color = (0, 0, 0, 255)
                    r = size / 2
                    center = x + r, y + r
                    for a in range(x, x + size):
                        for b in range(y, y + size):
                            vector = a - center[0], b - center[1]
                            highpot = hypot(*vector)
                            thresh = self.rands() + (highpot / r) * 0.5
                            peed = snoise2(ox / freq * 2, oy / freq * 2) * 0.2 + 0.1
                            if peed > thresh:
                                pixels[a, b] = color
                    #pixels[x + 1, y] = color
                    #pixels[x + 1, y + 1] = color
                    #pixels[x, y + 1] = color
        filename = '%s.png' % (str(uuid4())[:8])
        img.save('/tmp/' + filename)
        key = 'bg_%d_%d' % (ix, iy)
        image = self.textures.load(key, filename=filename, reindex=True)
        unlink('/tmp/' + filename)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        return key

    def seed(self, x, y):
        if not self.world.unseeded(x, y):
            return
        tl = self.world._alias(x, y)
        ax, ay = tuple(map(lambda z: z * self.world.chunk_size, tl))
        bounds = (ax, ay, ax + self.world.chunk_size, ay + self.world.chunk_size)
        cells = []

        def freq(perc):
            maxcell = (self.world.chunk_size / 32) * (self.world.chunk_size / 32) / 2
            res = int(maxcell * perc)
            return res

        def xy():
            xx = randint(bounds[0], bounds[2])
            yy = randint(bounds[1], bounds[3])
            xx = xx - xx % 16
            yy = yy - yy % 16
            return (
                xx, yy
                )

        uranium_freq = freq(.03)
        pine_freq = freq(.05)
        birch_freq = freq(.05)
        road_freq = freq(0.03)

        #dirt_chunk = self.world.chunk_size
        #for y in range(rect.top, rect.height, dirt_chunk):
        #    for x in range(rect.left, rect.width, dirt_chunk):
        #        dw = dirt_chunk
        #        dh = dirt_chunk
        #        if x + dw > rect.right:
        #            dw = rect.right - x
        #        if y + dh > rect.bottom:
        #            dh = rect.bottom - y
        #        if dw <= 0 or dh <= 0:
        #            continue
        #        print('creating dirt', x, y, dw, dh)
        #        #cells.append(Cell('dirt', self.textures, (x, y), 'dirt', size=(dw, dh),
        #        #    priority=-10))

        for i in range(uranium_freq):
            cells.append(Uranium(self.textures, xy()))
        for i in range(pine_freq):
            cells.append(PineTree(self.textures, xy()))
        for i in range(birch_freq):
            cells.append(BirchTree(self.textures, xy()))
        for i in range(road_freq):
            begin = xy()
            step = randint(0,1)
            step = -1 if step == 0 else step
            index = randint(0,1)
            number = randint(5,25)
            for c in range(0, number):
                if randint(0,100) < 15:
                    index = randint(0,1)
                newpos = list(begin)
                newpos[index] = 16 * c * step + begin[index]
                cells.append(RoadCell(self.textures, newpos))
        self.world.seed(*tl, [])
        self.deferred_inserts.extend(cells)
        image_key = self.create_background(bounds[0], bounds[1])
        bg_sprite = Sprite(self.textures[image_key], bounds[0], bounds[1])
        bg_sprite.scale = 2
        self.world.set_bg(bg_sprite, bounds[0], bounds[1])

        return True

