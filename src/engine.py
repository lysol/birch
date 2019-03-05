from random import choice, randint
from math import sin, pi
from pygame import Rect
from cells.rci import RCell, CCell, ICell
from cells.cell import Cell
from cells.connectable import ConnectableCell
from cells.road import RoadCell
from cells.rail import RailCell
from util import clamp, pi2
from quad import Quad

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

    def __init__(self, state, textures, dimensions=(128, 128)):
        self.dimensions = dimensions
        self.state = state
        self.ticks = 0
        self.textures = textures
        self._next_rci = 0
        self._demand_calc()
        self.quad = Quad(Rect(0, 0, *self.dimensions))

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

    # a way to cheat here is to make the quadtree leaf size 32.
    # this way we can get the top/left surrounding cells and figure out if we need
    # to return a cell that is oozing into this one
    def get_cell(self, rect):
        return self.quad.get(rect)
        #try:
        #    return self.state["cells"][y][x]
        #except IndexError:
        #    return None

    def set_cell(self, cell):
        apos = self.alias_pos(cell.rect[0], cell.rect[1])
        cell.rect[0] = apos[0]
        cell.rect[1] = apos[1]
        self.quad.insert(cell)
        self.state['cells'].append(cell)

    def del_cell(self, cell):
        self.quad.remove(cell)
        self.state['cells'].remove(cell)

    def alias_rect(self, rect):
        offset = [-(rect[0] % rect.width), -(rect[1] % rect.height)]
        return rect.move(offset)

    def alias_pos(self, x, y, size=16):
        return [
            x - x % size,
            y - y % size
            ]

    def use_tool(self, name, pos):
        tool_size = self.textures[name].get_size()
        rect32 = self.alias_rect(Rect(pos[0], pos[1], 32, 32))
        effect_rect = self.alias_rect(Rect(pos[0], pos[1], tool_size[0], tool_size[1]))
        intersected = self.get_cell(effect_rect)
        cells = list(filter(lambda c: c.impassible, intersected))

        new_cell = None
        if name == "bulldoze":
            for cell in cells:
                self.del_cell(cell)
            self.set_cell(Cell('dirt', self.textures, rect32))
        elif len(cells) == 0:
            for cell in intersected:
                if not cell.impassible:
                    self.del_cell(cell)
            if name == "r_0_0":
                new_cell = RCell(self.textures, pos)
            elif name == "c_0_0":
                new_cell = CCell(self.textures, pos)
            elif name == "i_0_0":
                new_cell = ICell(self.textures, pos)
            elif name == "road_h":
                new_cell = RoadCell(self.textures, pos)
            elif name == "rail_h":
                new_cell = RailCell(self.textures, pos)
        if new_cell is not None:
            self.set_cell(new_cell)
            if issubclass(type(new_cell), ConnectableCell):
                surrounding = self.quad.get(
                    new_cell.rect.inflate((new_cell.height * 2, new_cell.width * 2)))
                for cell in surrounding:
                    if type(cell) == type(new_cell):
                        cell.cache_texture(self.get_surrounding(cell))

