from random import choice, randint
from math import sin, pi
from collections import deque
from pygame import Rect
from birch.cells.rci import RCell, CCell, ICell
from birch.cells.cell import Cell
from birch.cells.connectable import ConnectableCell
from birch.cells.road import RoadCell
from birch.cells.rail import RailCell
from birch.cells.uranium import Uranium
from birch.cells.tree import PineTree, BirchTree
from birch.util import clamp, pi2
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
    insert_chunk = 25

    def __init__(self, state, textures, initial_rect):
        self.initial_rect = initial_rect
        self.state = state
        self.ticks = 0
        self.textures = textures
        self._next_rci = 0
        self._demand_calc()
        self.world = World()
        self.deferred_inserts = deque([])

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
        zone = cell.rect.copy().inflate(cell.width * 2, cell.height * 2)
        return self.world.get(*zone.topleft, zone.width, zone.height)

    def get_cell(self, rect):
        return self.world.get(*rect.topleft, rect.width, rect.height)

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
        return cells

    def set_cell(self, cell, alias=True, grow=True, defer=False):
        if alias:
            apos = self.alias_pos(cell.rect[0], cell.rect[1])
            cell.rect[0] = apos[0]
            cell.rect[1] = apos[1]
        if defer:
            self.deferred_inserts.append(cell)
        else:
            self.state['cells'].append(cell)
            self.world.insert(cell, *cell.position)

    def del_cell(self, cell):
        self.world.delete(cell, *cell.position)
        if cell in self.state['cells']:
            self.state['cells'].remove(cell)

    def alias_rect(self, rect):
        offset = [-(rect[0] % rect.width), -(rect[1] % rect.height)]
        return rect.move(offset)

    def alias_pos(self, x, y, size=16):
        return [
            x - x % size,
            y - y % size
            ]

    def use_tool(self, name, rect):
        tool_size = self.textures[name].get_size()
        intersected = self.get_cell(rect)
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
                new_cell = RCell(self.textures, rect.topleft)
            elif name == "c_0_0":
                new_cell = CCell(self.textures, rect.topleft)
            elif name == "i_0_0":
                new_cell = ICell(self.textures, rect.topleft)
            elif name == "road_h":
                new_cell = RoadCell(self.textures, rect.topleft)
            elif name == "rail_h":
                new_cell = RailCell(self.textures, rect.topleft)
        if new_cell is not None:
            self.set_cell(new_cell)
            if issubclass(type(new_cell), ConnectableCell):
                checkrect = new_cell.rect.inflate(new_cell.rect.width * 2,
                    new_cell.rect.height * 2)
                surrounding = self.world.get(
                    *checkrect.topleft, checkrect.width, checkrect.height)
                for cell in surrounding:
                    if type(cell) == type(new_cell):
                        cell.cache_texture(self.get_surrounding(cell))

    def get_batches(self, x, y, w, h):
        r = Rect(x, y, w, h).inflate(w, h)
        return self.world.get_batches(*r.topleft, r.width, r.height)

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

        self.world.seed(*tl, cells)
        return True

