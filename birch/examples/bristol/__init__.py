from birch.game import BirchGame
from random import shuffle, random
from birch._birch import Perlin
from birch.cells.blueprint import BlueprintCell
from birch.examples.bristol.cells.grass import ShortGrass

class Bristol:

    seed_config = {
        'short_grass': {
            'class': ShortGrass,
            'freq': 1/400,
            'octaves': 1,
            'offset': [110, -43],
            'threshold': 0.5,
            'rand_thresh': 0.95
            },
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
        self.game = BirchGame('birch/examples/bristol/assets')
        self.game.register_tick_handler(self.tick_handler)
        self.game.register_seed_handler(self.seed_handler)
        #self.game.register_mouse_handler(self.mouse_handler)
        #self.game.register_mouse_press_handler(self.mouse_press_handler)
        #self.game.register_map_click_handler(self.map_click_handler)
        self.game.camera_controlled = False
        self.game.player_controlled = True
        self.game.set_player('player')

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
                bounds[0], bounds[1], engine.world.chunk_size, engine.world.chunk_size,
                cfg['freq'], cfg['octaves'], 1.0, 32)
            for (oy, pees) in enumerate(perlins):
                for (ox, val) in enumerate(pees):
                    ix = bounds[0] + ox * 32
                    iy = bounds[1] + oy * 32
                    if val > cfg['threshold'] and (cfg['rand_thresh'] == 0 or random() > cfg['rand_thresh']):
                        cells.append(BlueprintCell(cfg['class'], (engine.textures, (ix, iy))))

        return cells

    def run(self):
        self.game.run()

if __name__ == '__main__':
    bristol = Bristol()
    bristol.run()

