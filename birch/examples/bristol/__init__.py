from birch import CHUNK_SIZE#, svgcell
from birch.game import BirchGame
from random import shuffle, random, randint, uniform
from birch._birch import Perlin
from birch.cells.blueprint import BlueprintCell
from birch.examples.bristol.cells.grass import ShortGrass
from birch.examples.bristol.cells.water import Water
from pyglet import sprite

class Bristol:

    seed_config = {
        'short_grass': {
            'class': ShortGrass,
            'freq': 1/10,
            'octaves': 1,
            'offset': [110, -43],
            'threshold': 0.1,
            'rand_thresh': 0.93
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

    def __init__(self):
        self.ticks = 0
        self.perlin = Perlin(999)
        self.game = BirchGame('examples/bristol/assets')
        self.game.register_tick_handler(self.tick_handler)
        self.game.register_seed_handler(self.seed_handler)
        #self.game.register_mouse_handler(self.mouse_handler)
        #self.game.register_mouse_press_handler(self.mouse_press_handler)
        #self.game.register_map_click_handler(self.map_click_handler)
        self.game.camera_controlled = False
        self.game.player_controlled = True
        self.game.set_player('player')
        self.game.player.speed = 3
        self.rivers = []

    def make_water(self, position):
        return BlueprintCell(Water, (self.game.engine.textures, position))

    def seed_handler(self, engine, bounds):
        seed_config = self.seed_config
        cells = []
        seed_keys = list(seed_config.keys())
        shuffle(seed_keys)
        for key in seed_keys:
            cfg = seed_config[key]
            perlins = self.perlin.perlin_octave_array(
                bounds.left, bounds.top, CHUNK_SIZE, CHUNK_SIZE,
                cfg['freq'], cfg['octaves'], 1.0, 32)
            for (oy, pees) in enumerate(perlins):
                for (ox, val) in enumerate(pees):
                    ix = bounds.left + ox * 32
                    iy = bounds.top + oy * 32
                    if val > cfg['threshold'] and (cfg['rand_thresh'] == 0 or random() > cfg['rand_thresh']):
                        cells.append(BlueprintCell(cfg['class'], (engine.textures, (ix, iy))))

        #waters = svgcell.cell_layer(engine.textures.asset_dir + '/water/water',
        #        bounds.left, bounds.top, CHUNK_SIZE, self.make_water)
        #cells.extend(waters)
        image_key = engine.textures.create_background(
            int(CHUNK_SIZE / 2),
            int(bounds.left / 2),
            int(bounds.top / 2))
        bg_sprite = sprite.Sprite(engine.textures[image_key], bounds.left, bounds.top)
        bg_sprite.scale = 2
        engine.world.set_bg(bg_sprite, bounds.left, bounds.top)
        return cells

    def run(self):
        self.game.run()

if __name__ == '__main__':
    bristol = Bristol()
    bristol.run()

