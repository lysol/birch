from random import choice, randint
from math import sin, pi
from cells.rci import RCell, CCell, ICell
from cells.cell import Cell
from util import clamp, pi2

class Engine:

    freqs = {
        "r": 10000,
        "c": 8000,
        "i": 5000
        }

    freq_factor = 0.25

    demand_offset = {
        "r": 5000,
        "c": 0,
        "i": 2500
        }

    ratios = {
        "r": {
            "r": 0,
            "c": 1,
            "i": -5
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

    overall_factor = 0.2

    rci_interval = 20

    def __init__(self, state, textures):
        self.state = state
        self.ticks = 0
        self.textures = textures
        self._next_rci = 0

    def tick(self):
        damage = False
        self.ticks += self.state["speed"]
        changed = []
        for row in self.state["cells"]:
            for cell in filter(lambda c: c.next_tick <= self.ticks, row):
                if cell.tick(self.ticks, self):
                    # Use the state reference because otherwise if the cell
                    # was destroyed, this will be the old one.
                    changed.append(cell.position)
        self.state["demand"] = {}
        for ckey in self.freqs:
            # use a sine wave to express demand waves
            self.state["demand"][ckey] = \
                (sin(
                    # current time mod celltype frequency to get cycle 0 - 1
                    self.ticks % self.freqs[ckey] / float(self.freqs[ckey]) * \
                    # additional modifier to change speed as a whole
                    self.freq_factor * \
                    # it's like pi, but twice as much
                    pi2) + \
                    # shift it positive, rescale it 0 - 1
                    1.0) / 2.0
        if self._next_rci <= self.ticks:
            self._rci()
            self._next_rci = self.ticks + self.rci_interval
        return changed

    def _rci(self):
        rci = ['r','c','i']
        workcells = {k: [] for k in rci}
        self.state["population"] = 0
        for row in self.state["cells"]:
            for cell in row:
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
                if randint(0, 100) < 25:
                    cell.populate()
                    cell.level_check()
                neighbors = self.get_surrounding(*cell.position)
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
                demand = clamp(round(demand + self.state["demand"][ckey] * self.overall_factor), -1, 1)
                cell.demand = demand

    def get_surrounding(self, x, y):
        yes = list(range(y - 1, y + 2))
        xes = list(range(x - 1, x + 2))
        output = []
        for yy in yes:
            for xx in xes:
                if yy != y and xx != x:
                    output.append(self.get_cell(xx, yy))
        return list(filter(lambda x: x is not None, output))

    def get_cell(self, x, y):
        try:
            return self.state["cells"][y][x]
        except IndexError:
            return None

    def set_cell(self, x, y, cell):
        self.state["cells"][y][x] = cell

    def use_tool(self, name, pos):
        cell = self.get_cell(*pos)
        if cell is None:
            return
        if name == "bulldoze":
            if cell.name != "dirt":
                self.set_cell(pos[0], pos[1],
                    Cell("dirt", self.textures, pos))
        elif name == "r_0_0":
            if cell.name == "dirt":
                self.set_cell(pos[0], pos[1],
                    RCell(self.textures, pos))

        elif name == "c_0_0":
            if cell.name == "dirt":
                self.set_cell(pos[0], pos[1],
                    CCell(self.textures, pos))

        elif name == "i_0_0":
            if cell.name == "dirt":
                self.set_cell(pos[0], pos[1],
                    ICell(self.textures, pos))

