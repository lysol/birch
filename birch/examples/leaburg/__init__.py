from birch.game import BirchGame
from birch.tiledworld import TiledWorld
from random import shuffle, random, randint, uniform
from birch._birch import Perlin
from birch.cells.blueprint import BlueprintCell

import os

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
        self.world = TiledWorld(['birch/examples/leaburg/maps/dam.json'])
        self.game = BirchGame('birch/examples/leaburg/assets', world=self.world)
        self.game.register_tick_handler(self.tick_handler)
        self.game.register_player_move_handler(self.world.collision_check)
        #self.game.register_mouse_handler(self.mouse_handler)
        #self.game.register_mouse_press_handler(self.mouse_press_handler)
        #self.game.register_map_click_handler(self.map_click_handler)
        self.game.camera_controlled = False
        self.game.player_controlled = True
        self.game.set_player('player', position=(64, 500 * 64))
        self.game.player.speed = 4
        self.world.set_engine(self.game.engine)
        self.world.spawn_maps()

    def run(self):
        self.game.run()

if __name__ == '__main__':
    leaburg = Leaburg()
    leaburg.run()

