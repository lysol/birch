from birch.game import BirchGame
from birch.tiledworld import TiledWorld
from random import shuffle, random, randint, uniform
from birch._birch import Perlin
from birch.cells.blueprint import BlueprintCell
from birch.examples.leaburg.cells.grass import Grass
from birch.examples.leaburg.cells.small_spikes import SmallSpikes
from birch.examples.leaburg.cells.spikes import Spikes
from birch.examples.leaburg.cells.flower import Flower

import os

celldict = {
    'Grass': Grass,
    'SmallSpikes': SmallSpikes,
    'Spikes': Spikes,
    'Flower': Flower
    }

class Leaburg:

    @property
    def state(self):
        return self.game.engine.state

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
        self.world = TiledWorld(['birch/examples/leaburg/maps/dam.json'], celldict)
        self.game = BirchGame('birch/examples/leaburg/assets', self.world)
        self.game.register_tick_handler(self.tick_handler)
        #self.game.register_mouse_handler(self.mouse_handler)
        #self.game.register_mouse_press_handler(self.mouse_press_handler)
        #self.game.register_map_click_handler(self.map_click_handler)
        self.game.camera_controlled = False
        self.game.player_controlled = True
        self.game.set_player('player', position=(64, 500 * 64))
        self.world.set_engine(self.game.engine)
        self.world.spawn_maps()

    def run(self):
        self.game.run()

if __name__ == '__main__':
    leaburg = Leaburg()
    leaburg.run()

