from os import unlink
from random import choice, randint, random, shuffle
from math import sin, pi, hypot
from collections import deque
from uuid import uuid4
from datetime import datetime, timedelta
from pyglet.gl import *
from pyglet import resource
from pyglet.sprite import Sprite
from pyglet.image import Texture, ImageData
import pyglet
from PIL import Image, ImageDraw
from birch.cells.rci import RCell, CCell, ICell
from birch.cells.cell import Cell
from birch.cells.blueprint import BlueprintCell
from birch.cells.connectable import ConnectableCell
from birch.cells.road import RoadCell
from birch.cells.rail import RailCell
from birch.cells.water import WaterCell
from birch.cells.uranium import Uranium
from birch.cells.tree import PineTree, BirchTree
from birch.util import clamp, pi2, Rect
from birch.world import World
from birch._birch import Perlin

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

    rci_interval = 40
    cell_rci_interval = 80
    max_rci_per_tick = 25

    cell_minimum = 16
    insert_chunk = 15

    seed_config = {
        'birch_tree': {
            'class': BirchTree,
            'freq': 1/400,
            'octaves': 1,
            'offset': [110, -43],
            'threshold': 0.5,
            'rand_thresh': 0.95
            },
        'pine_tree': {
            'class': PineTree,
            'freq': 1/1400,
            'octaves': 1,
            'offset': [-1277, 76],
            'threshold': 0.6,
            'rand_thresh': 0.95
            },
        'water': {
            'class': WaterCell,
            'freq': 1/1560,
            'octaves': 2,
            'offset': [-999, -321],
            'threshold': 0.7,
            'rand_thresh': 0.0
            }
        }

    def __init__(self, state, textures):
        self.state = state
        self.ticks = 0
        self.textures = textures
        self._next_rci = self.rci_interval
        self._demand_calc()
        self.world = World()
        self.deferred_inserts = deque([])
        self.perlin = Perlin(818)

    def in_range(self, camera, pos):
        return pos[0] > camera[0] - 1000 or \
            pos[0] < camera[0] + 1000 or \
            pos[1] < camera[1] - 1000 or \
            pos[1] < camera[1] + 1000

    def tick(self, dt, checkrect=None):
        damage = False
        self.ticks += self.state["speed"]
        changed = []
        if self._next_rci <= self.ticks:
            self._demand_calc()
            self._rci()
            self._next_rci = self.ticks + self.rci_interval
        if len(self.deferred_inserts) > 0:
            inserted = self.do_insert()
            checkrect.inflate_in_place(checkrect.width, checkrect.height)
            if checkrect is not None:
                for item in inserted:
                    if checkrect.colliderect(item.rect):
                        changed.append(item)
            else:
                changed.extend(inserted)
        for cell in self.state["cells"]:
            if cell.next_update != -1 and self.ticks >= cell.next_update:
                cell.update(self.ticks, self)
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
        workcells = []
        self.state["population"] = 0
        to_check = [RCell, CCell, ICell]
        # we could index these by type somewhere else for
        # more speed later
        for cell in self.state["cells"]:
            if type(cell) in to_check:
                workcells.append(cell)
            if hasattr(cell, 'population'):
                self.state["population"] += cell.population
        if len(workcells) == 0:
            return False
        targets = []
        for yarp in range(self.max_rci_per_tick):
            targets.append(choice(workcells))
        for cell in targets:
            if cell.last_rci + self.cell_rci_interval > self.ticks:
                # not ready yet :)
                continue
            if type(cell) is RCell:
                ckey = 'r'
            elif type(cell) is CCell:
                ckey = 'c'
            elif type(cell) is ICell:
                ckey = 'i'
            if randint(0, 100) < 25 * abs(cell.demand):
                cell.populate()
                cell.level_check()
                cell.last_rci = self.ticks
            neighbors = self.world.get_surrounding(cell, workcells)
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
            global_demand = self.state['demand'][ckey] - 0.5
            demand = clamp(demand + global_demand * self.overall_factor, -1, 1)
            cell.demand = demand

    def get_cell(self, x, y, w, h):
        return self.world.get(x, y, w, h)

    def do_insert(self):
        cells = []
        for z in range(self.insert_chunk):
            if len(self.deferred_inserts) == 0:
                break
            bp = self.deferred_inserts.popleft()
            cells.append(bp.to_cell())
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
            newbounds = cell.rect.inflate(cell.width * 4, cell.height * 4).bounds
            innerrect = cell.rect.inflate(cell.width * 2, cell.height * 2)
            surrounding = self.world.get(*newbounds)
            for other in surrounding:
                if type(other) == type(cell) and other.rect.colliderect(innerrect):
                    other.cache_texture(surrounding)

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
            elif name == "rail_h":
                new_cell = RailCell(self.textures, (x, y))
            elif name == "road_h":
                new_cell = RoadCell(self.textures, (x, y))
            elif name == "water_o_0":
                new_cell = WaterCell(self.textures, (x, y))
        if new_cell is not None:
            self.set_cell(new_cell, alias=False)

    def get_batches(self, x, y, w=1, h=1):
        r = Rect(x, y, w, h)
        r.inflate_in_place(w, h)
        return self.world.get_batches(*r.topleft, r.width, r.height)

    def seed(self, x, y):
        if not self.world.unseeded(x, y):
            return
        seed_config = self.seed_config

        tl = self.world._alias(x, y)
        ax, ay = tuple(map(lambda z: z * self.world.chunk_size, tl))
        bounds = (ax, ay, ax + self.world.chunk_size, ay + self.world.chunk_size)
        cells = []
        seed_keys = list(seed_config.keys())
        shuffle(seed_keys)
        for key in seed_keys:
            cfg = seed_config[key]
            perlins = self.perlin.perlin_octave_array(
                bounds[0], bounds[1], self.world.chunk_size, self.world.chunk_size,
                cfg['freq'], cfg['octaves'], 1.0, 16)
            for (oy, pees) in enumerate(perlins):
                for (ox, val) in enumerate(pees):
                    ix = bounds[0] + ox * 16
                    iy = bounds[1] + oy * 16
                    if val > cfg['threshold'] and (cfg['rand_thresh'] == 0 or random() > cfg['rand_thresh']):
                        cells.append(BlueprintCell(cfg['class'], (self.textures, (ix, iy))))
        self.world.seed(*tl, [])
        self.deferred_inserts.extend(cells)
        image_key = self.textures.create_background(
            int(self.world.chunk_size / 2),
            int(bounds[0] / 2),
            int(bounds[1] / 2))
        bg_sprite = Sprite(self.textures[image_key], bounds[0], bounds[1])
        bg_sprite.scale = 2
        self.world.set_bg(bg_sprite, bounds[0], bounds[1])

        return True

