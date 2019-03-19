import pyglet
from birch.texture_store import TextureStore
from birch.toolbox import Toolbox
from birch.statusbox import Statusbox
from birch.rcibox import RCIbox
from birch.engine import Engine
from birch.util import RED, BLUE, FG_COLOR, BG_COLOR
from birch import cursor

class BirchWindow(pyglet.window.Window):

    def on_draw(self):
        self.clear()


class BirchGame:

    def __init__(self, initial_rect, asset_dir):
        self.size = 800, 600
        self.asset_dir = asset_dir
        self.textures = TextureStore(asset_dir)
        self.window = BirchWindow(width=self.size[0], height=self.size[1])
        self.initial_rect = initial_rect
        self.engine = Engine({
            "cells": [],
            "money": 10000,
            "population": 0,
            "speed": 1
            }, self.textures, initial_rect)

    def run(self):
        pyglet.clock.schedule_interval(self.update, 0.5)
        pyglet.app.run()

    def update(self, dt):
        pass

