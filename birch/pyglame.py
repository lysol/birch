import pyglet, json
from pyglet.window import key
from pyglet.gl import *
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

    def __init__(self, batch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = batch

    def on_draw(self):
        self.clear()
        pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
            [0, 1, 2, 0, 2, 3],
            ('v2i', (0, 0,
                     self.width, 0,
                     self.width, self.height,
                     0, self.height)),
            ('c3B', (
                255, 255, 255,
                255, 255, 255,
                255, 255, 255,
                255, 255, 255))
        )
        self.batch.draw()


class BirchGame:

    camera_speed = 2

    def __init__(self, initial_rect, asset_dir):
        self.size = 800, 600
        self.asset_dir = asset_dir
        self.batch = pyglet.graphics.Batch()
        self.textures = TextureStore(asset_dir, self.batch)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.window = BirchWindow(self.batch, width=self.size[0], height=self.size[1])
        self.window.set_caption('birch')
        self.window.set_icon(self.textures['birch_tree'])
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
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)


    def run(self):
        self.engine.seed()
        pyglet.clock.schedule_interval(self.update, 1/120.0)
        pyglet.app.run()
        #self.init_panels()

    def update(self, dt):
        self.engine.tick()
        if self.keys[key.LEFT]:
            self.camera[0] -= self.camera_speed
        if self.keys[key.RIGHT]:
            self.camera[0] += self.camera_speed
        if self.keys[key.DOWN]:
            self.camera[1] += self.camera_speed
        if self.keys[key.UP]:
            self.camera[1] -= self.camera_speed
        print(self.camera)

