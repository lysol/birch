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

    def __init__(self, batches, ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batches = batches
        self.ui = ui
        self.handlers = {}
        self.camera = (0, 0)

    def on_draw(self):
        self.clear()
        left = 0
        top = 0
        right = self.width
        bottom = self.height
        self.change_view(camera=(0, 0))
        pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
            [0, 1, 2, 0, 2, 3],
            ('v2i', (left, top,
                     right, top,
                     right, bottom,
                     left, bottom)),
            ('c3B', (
                255, 255, 255,
                255, 255, 255,
                255, 255, 255,
                255, 255, 255))
        )
        self.change_view()
        for batch in self.batches:
            batch.draw()
        self.change_view(camera=(0, 0))
        for el in self.ui:
            el.draw()

    def handle(self, key, handler):
        if key not in self.handlers:
            self.handlers[key] = []
        self.handlers[key].append(handler)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        if 'resize' in self.handlers:
            for handler in self.handlers['resize']:
                handler(width, height)

    def on_mouse_motion(self, x, y, dx, dy):
        if 'mouse' in self.handlers:
            for handler in self.handlers['mouse']:
                handler(x, self.width - y, dx, dy)

    def change_view(self, width=None, height=None, camera=None):
        camera = self.camera if camera is None else camera
        width = width if width is not None else self.width
        height = height if height is not None else self.height
        left = camera[0]
        top = camera[1]
        right = camera[0] + width
        bottom = camera[1] + height
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(left, right, top, bottom, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)


class BirchGame:

    camera_speed = 16

    def __init__(self, initial_rect, asset_dir):
        pyglet.options['debug_gl'] = False
        self.size = 800, 600
        self.asset_dir = asset_dir
        self.textures = TextureStore(asset_dir)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.ui_elements = []
        self.window = BirchWindow([], self.ui_elements, width=self.size[0], height=self.size[1])
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
        self.last_camera = [-1000000, -1000000]
        self.cursor_speed = 8
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
        self.window.handle('mouse', self.handle_mouse)
        #self.window.handle('resize', self.handle_resize)
        self.init_ui()

    def init_ui(self):
        self.ui_elements.append(Toolbox(self.window.height, self.textures))

    def run(self):
        self.engine.seed(0, 0)
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()
        #self.init_panels()

    def handle_mouse(self, x, y, dx, dy):
        self.mouse = x, y

    @property
    def camera_rect(self):
        return Rect(self.camera[0], self.camera[1], self.size[0], self.size[1]
                )

    #def handle_resize(self, width, height):
    #    self.change_view(width, height)

    def update(self, dt):
        self.engine.tick(checkrect=self.camera_rect)
        view_changed = False
        for point in (self.camera_rect.topleft, self.camera_rect.topright,
            self.camera_rect.bottomleft, self.camera_rect.bottomright):
            self.engine.seed(*point)
        if self.keys[key.LEFT]:
            self.camera[0] -= self.camera_speed
            view_changed = True
        if self.keys[key.RIGHT]:
            self.camera[0] += self.camera_speed
            view_changed = True
        if self.keys[key.UP]:
            self.camera[1] += self.camera_speed
            view_changed = True
        if self.keys[key.DOWN]:
            self.camera[1] -= self.camera_speed
            view_changed = True
        delta = abs(self.camera[0] - self.last_camera[0]) + \
                abs(self.camera[1] - self.last_camera[1])
        if delta > self.camera_speed * 2 or not self.first:
            self.window.batches = self.engine.get_batches(*self.camera,
                self.camera_rect.width, self.camera_rect.height)
            self.last_camera = list(self.camera)
            self.first = True
        self.window.camera = self.camera

