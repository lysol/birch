import pyglet, json
from birch.texture_store import TextureStore
from birch.toolbox import Toolbox
from birch.statusbox import Statusbox
from birch.rcibox import RCIbox
from birch.engine import Engine
from birch.util import RED, BLUE, FG_COLOR, BG_COLOR
from birch import cursor


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        else:
            return repr(o)


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
        self.mouse_down = [False, False]
        self.scroll_speed = [2, 2]
        self.camera = [-400, -300]
        self.camera_speed = 12
        self.cursor_speed = 8
        self.screen = None
        self.fps = 60
        self.sleeptime = 1 / self.fps
        self.time_spent = 0
        self.kf_interval = 0.5
        self.speed_delay = 0.1
        self.edge_delay = 0.5
        self.scroll_pos = 0, 0
        self.jsonenc = ObjectEncoder()

    def run(self):
        self.engine.seed()
        pyglet.clock.schedule_interval(self.update, 0.5)
        pyglet.app.run()
        #self.init_panels()

    def update(self, dt):
        pass

