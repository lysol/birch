from math import sin, pi
from random import choice, randint, shuffle, random
from pyglet.sprite import Sprite
from birch import CHUNK_SIZE
from birch.game import BirchGame
from birch.cells.cell import Cell
from birch.cells.connectable import ConnectableCell
from birch.cells.blueprint import BlueprintCell
from birch.examples.scamcity.toolbox import Toolbox
from birch.examples.scamcity.statusbox import Statusbox
from birch.examples.scamcity.rcibox import RCIbox
from birch.examples.scamcity.cells.rci import RCell, CCell, ICell
from birch.examples.scamcity.cells.road import RoadCell
from birch.examples.scamcity.cells.rail import RailCell
from birch.examples.scamcity.cells.water import WaterCell
from birch.examples.scamcity.cells.brick_halfwall import BrickHalfWallCell
from birch.examples.scamcity.cells.brick_wall import BrickWallCell
from birch.examples.scamcity.cells.uranium import Uranium
from birch.examples.scamcity.cells.tree import PineTree, BirchTree
from birch._birch import Perlin
from birch.util import clamp, pi2, Rect

class ScamCity:

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

    @property
    def state(self):
        return self.game.engine.state

    @property
    def world(self):
        return self.game.engine.world

    @property
    def textures(self):
        return self.game.engine.textures

    @property
    def engine(self):
        return self.game.engine

    def get_cell(self, *args, **kwargs):
        return self.game.engine.get_cell(*args, **kwargs)

    def del_cell(self, *args, **kwargs):
        return self.game.engine.del_cell(*args, **kwargs)

    def set_cell(self, *args, **kwargs):
        return self.game.engine.set_cell(*args, **kwargs)

    def tick_handler(self, engine, rt, ticks):
        self.ticks = ticks
        if self._next_rci <= self.ticks:
            self._demand_calc()
            self._rci()
            self._next_rci = self.ticks + self.rci_interval
        self.rcibox.r = engine.state["demand"]["r"]
        self.rcibox.c = engine.state["demand"]["c"]
        self.rcibox.i = engine.state["demand"]["i"]

    def mouse_handler(self, x, y, dx, dy):
        pass

    def mouse_drag_handler(self, x, y, dx, dy, button, modifiers):
        self.game.set_cursor_size(self.toolbox.tool_size)

    def mouse_press_handler(self, x, y, button, modifiers):
        self.game.set_cursor_size(self.toolbox.tool_size)

    def seed_handler(self, engine, boundsRect):
        seed_config = self.seed_config
        bounds = (
            boundsRect.left, boundsRect.top,
            boundsRect.right, boundsRect.bottom
            )
        cells = []
        seed_keys = list(seed_config.keys())
        shuffle(seed_keys)
        for key in seed_keys:
            cfg = seed_config[key]
            perlins = self.perlin.perlin_octave_array(
                bounds[0], bounds[1], CHUNK_SIZE, CHUNK_SIZE,
                cfg['freq'], cfg['octaves'], 1.0, 16)
            for (oy, pees) in enumerate(perlins):
                for (ox, val) in enumerate(pees):
                    ix = bounds[0] + ox * 16
                    iy = bounds[1] + oy * 16
                    if val > cfg['threshold'] and (cfg['rand_thresh'] == 0 or random() > cfg['rand_thresh']):
                        cells.append(BlueprintCell(cfg['class'], (engine.textures, (ix, iy))))
        image_key = engine.textures.create_background(
            int(CHUNK_SIZE / 2),
            int(bounds[0] / 2),
            int(bounds[1] / 2))
        bg_sprite = Sprite(engine.textures[image_key], bounds[0], bounds[1])
        bg_sprite.scale = 2
        engine.world.set_bg(bg_sprite, bounds[0], bounds[1])

        return cells

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

    def map_click_handler(self, x, y):
        self.use_tool(self.toolbox.selected, x, y,
            tool_size=self.toolbox.tool_size)

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
            elif name == "rail_h_0":
                new_cell = RailCell(self.textures, (x, y))
            elif name == "road_h_0":
                new_cell = RoadCell(self.textures, (x, y))
            elif name == "water_o_0":
                new_cell = WaterCell(self.textures, (x, y))
            elif name == "brick_halfwall_o_0":
                new_cell = BrickHalfWallCell(self.textures, (x, y))
            elif name == "brick_wall_o_0":
                new_cell = BrickWallCell(self.textures, (x, y))
        if new_cell is not None:
            self.set_cell(new_cell, alias=False)

    def __init__(self):
        self.ticks = 0
        self.game = BirchGame('birch/examples/scamcity/assets')
        self.game.set_caption('birch')
        self.game.set_icon(self.textures['birch_tree'])
        self.game.textures['r_1_0'] = self.game.textures['r_0_0']
        self.game.textures['c_1_0'] = self.game.textures['c_0_0']
        self.game.textures['i_1_0'] = self.game.textures['i_0_0']
        self.perlin = Perlin(818)
        self._next_rci = self.rci_interval
        self._demand_calc()
        self.game.register_tick_handler(self.tick_handler)
        self.game.register_seed_handler(self.seed_handler)
        self.game.register_mouse_handler(self.mouse_handler)
        self.game.register_mouse_press_handler(self.mouse_press_handler)
        self.game.register_map_click_handler(self.map_click_handler)

        self.toolbox = Toolbox(self.game.window.height, self.textures, self.game.main_batch)
        self.toolbox.set_tool('bulldoze')
        sx, sy = self.toolbox.x + self.toolbox.width + 4, self.toolbox.y
        self.statusbox = Statusbox(sx, sy, self.game.window.height, self.textures, self.engine, self.game.main_batch)
        zx, zy = self.toolbox.x, self.toolbox.y + self.toolbox.height + 4
        self.rcibox = RCIbox(zx, zy, self.game.window.height, self.game.main_batch, width=self.toolbox.width)

        self.game.ui_elements.append(self.toolbox)
        self.game.ui_elements.append(self.statusbox)
        self.game.ui_elements.append(self.rcibox)
        self.game.camera_controlled = True

    def run(self):
        self.game.run()

if __name__ == '__main__':
    scam = ScamCity()
    scam.run()
