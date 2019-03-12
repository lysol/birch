from random import choice, randint
from math import sin, pi
from pygame import Rect
from birch.cells.rci import RCell, CCell, ICell
from birch.cells.cell import Cell
from birch.cells.connectable import ConnectableCell
from birch.cells.road import RoadCell
from birch.cells.rail import RailCell
from birch.cells.uranium import Uranium
from birch.cells.tree import PineTree, BirchTree
from birch.util import clamp, pi2
from birch.quad import Quad
from birch.exceptions import QuadAlreadySeededException

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
    insert_chunk = 50

    def __init__(self, state, textures, initial_rect):
        self.initial_rect = initial_rect
        self.state = state
        self.ticks = 0
        self.textures = textures
        self._next_rci = 0
        self._demand_calc()
        self.quad = Quad(initial_rect)
        self.deferred_inserts = []

    def tick(self):
        damage = False
        self.ticks += self.state["speed"]
        changed = []
        for cell in filter(lambda c: c.next_tick <= self.ticks, self.state["cells"]):
            if cell.tick(self.ticks, self):
                # Use the state reference because otherwise if the cell
                # was destroyed, this will be the old one.
                changed.append(cell)
        if self._next_rci <= self.ticks:
            self._demand_calc()
            self._rci()
            self._next_rci = self.ticks + self.rci_interval
        if len(self.deferred_inserts) > 0:
            changed.extend(self.do_insert())
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
        return self.quad.get(Rect(zone))

    def get_cell(self, rect):
        return self.quad.get(rect)

    def do_insert(self):
        changed = []
        for z in range(self.insert_chunk):
            if len(self.deferred_inserts) == 0:
                break
            cell = self.deferred_inserts.pop(0)
            self.state['cells'].append(cell)
            self.quad.insert(cell)
            changed.append(cell)
        return changed

    def set_cell(self, cell, alias=True, grow=True, defer=False):
        if alias:
            apos = self.alias_pos(cell.rect[0], cell.rect[1])
            cell.rect[0] = apos[0]
            cell.rect[1] = apos[1]
        if grow:
            while self.quad.item_outside(cell):
                for point in (
                    cell.topleft, cell.topright, cell.bottomleft, cell.bottomright, cell.center
                ):
                    self.grow_check(point)
        if defer:
            self.deferred_inserts.append(cell)
        else:
            self.state['cells'].append(cell)
            self.quad.insert(cell)

    def del_cell(self, cell):
        self.quad.remove(cell)
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
                surrounding = self.quad.get(
                    new_cell.rect.inflate((new_cell.height * 2, new_cell.width * 2)))
                for cell in surrounding:
                    if type(cell) == type(new_cell):
                        cell.cache_texture(self.get_surrounding(cell))

    def seed(self, quad=None, point=None):
        self.quad._debug('seeding')
        if quad is None:
            quad = self.quad
        if quad.meta_is('seeded'):
            return True
        elif point is not None and not quad.rect.collidepoint(point):
            return False
        elif not quad.leaf:
            seeded = []
            for qu in quad.quarters:
                seeded.append(self.seed(qu))
            if seeded == [True, True, True, True]:
                quad.set_meta('seeded', True)
                return True
            else:
                return False

        rect = quad.rect
        cells = []

        for item in quad.items:
            shrink1 = quad.rect.inflate((-1, -1))
            if shrink1.collidepoint(item.rect.topleft):
                # should not be in here
                raise QuadAlreadySeededException(quad)

        def freq(perc):
            maxcell = (rect.width / 32) * (rect.width / 32) / 2
            res = int(maxcell * perc)
            return res

        def xy():
            x = randint(rect.left, rect.right - 1)
            y = randint(rect.top, rect.bottom - 1)
            x = x - x % 16
            y = y - y % 16
            return (
                x, y
                )

        uranium_freq = freq(.03)
        pine_freq = freq(.05)
        birch_freq = freq(.05)
        dirt_freq = freq(.2)

        for i in range(uranium_freq):
            cells.append(Uranium(self.textures, xy()))
        for i in range(pine_freq):
            cells.append(PineTree(self.textures, xy()))
        for i in range(birch_freq):
            cells.append(BirchTree(self.textures, xy()))
        for i in range(dirt_freq):
            cells.append(Cell('dirt', self.textures, xy()))

        quad.set_meta('seeded', True)
        for cell in cells:
            quad._debug('seed insert', cell.id, cell.rect)
            self.set_cell(cell, alias=False, grow=False, defer=True)
        return True

    def grow_check(self, point):
        changed = False
        while self.quad.point_outside(point):
            old_quad = self.quad
            self.quad = self.quad.grow(point)
            changed = True
        if changed:
            try:
                self.seed(self.quad, point=point)
            except QuadAlreadySeededException as e:
                self.quad.dump_seeded()
                raise e
