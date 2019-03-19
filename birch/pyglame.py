import pyglet, json
from pyglet.window import key
from pyglet.gl import *
from pygame import Rect
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

    def __init__(self, batches, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batches = batches

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
        for batch in self.batches:
            batch.draw()


class BirchGame:

    camera_speed = 2

    def __init__(self, initial_rect, asset_dir):
        pyglet.options['debug_gl'] = False
        self.size = 800, 600
        self.asset_dir = asset_dir
        self.textures = TextureStore(asset_dir)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.window = BirchWindow([], width=self.size[0], height=self.size[1])
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
        self.last_camera = [-1000000, -1000000]
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
        self.first = True

    def run(self):
        self.engine.seed()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()
        #self.init_panels()

    @property
    def camera_rect(self):
        return Rect(self.camera[0], self.camera[1], self.size[0], self.size[1]
                )

    def update(self, dt):
        self.engine.tick(checkrect=self.camera_rect)
        for point in (self.camera_rect.topleft, self.camera_rect.topright,
            self.camera_rect.bottomleft, self.camera_rect.bottomright):
            self.engine.grow_check(point)
        if self.keys[key.LEFT]:
            self.camera[0] -= self.camera_speed
        if self.keys[key.RIGHT]:
            self.camera[0] += self.camera_speed
        if self.keys[key.UP]:
            self.camera[1] += self.camera_speed
        if self.keys[key.DOWN]:
            self.camera[1] -= self.camera_speed
        delta = abs(self.camera[0] - self.last_camera[0]) + \
                abs(self.camera[1] - self.last_camera[1])
        if delta > 50 or self.first:
            self.last_camera = list(self.camera)
            self.window.batches = self.engine.get_batches(
                self.camera_rect.inflate(
                    self.camera_rect.width, self.camera_rect.height))
            self.first = True

