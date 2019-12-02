import math, json
import pyglet
import os
from pyglet.window import key
from pyglet.gl import *
from birch import CHUNK_SIZE
from birch.texture_store import TextureStore
from birch.cells.player import Player
from birch.cursor import Cursor
from birch.engine import Engine
from birch.util import RED, BLUE, FG_COLOR, BG_COLOR, Rect


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        else:
            return repr(o)


class BirchWindow(pyglet.window.Window):

    max_zoom = 2.0
    min_zoom = 1

    def __init__(self, batches, main_batch, ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batches = batches
        self.main_batch = main_batch
        self.ui = ui
        self.handlers = {}
        self.camera = (0, 0)
        self.zoom = 1
        self.reference_point = 0, 0
        self.cursor = None
        self.debug = False

    def on_draw(self):
        self.clear()
        left = 0
        top = 0
        right = self.width
        bottom = self.height
        self.change_view(zoom=1.0, camera=(0, 0))
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
        if self.debug:
            for y in range(0, self.height, 64):
                for x in range(0, self.width, 64):
                    delto = x, y
                    color = (255, 0, 0) if delto[0] % 128 == 0 and delto[1] % 128 == 0 else (0, 255, 0)
                    if delto[0] == 0 and delto[1] == 0:
                        color = (255, 255, 0)
                    self.draw_dot(x, y, color)
        if 'draw' in self.handlers:
            for handler in self.handlers['draw']:
                handler(self)
        self.change_view(zoom=1.0, camera=(0, 0))
        self.main_batch.draw()

    def draw_dot(self, x, y, color, width=3):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v2i', (
                x - width, y - width,
                x - width, y + width,
                x + width, y + width,
                x + width, y - width)),
            ('c3B', color * 4))

    def handle(self, key, handler):
        if key not in self.handlers:
            self.handlers[key] = []
        self.handlers[key].append(handler)

    def dispatch(self, key, *args, **kwargs):
        if key in self.handlers:
            for handler in self.handlers[key]:
                handler(*args, **kwargs)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.dispatch('resize', width, height)

    def on_mouse_motion(self, x, y, dx, dy):
        self.dispatch('mouse_motion', x, self.height - y, dx, -dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.reference_point = self.camera[0] + x, self.camera[1] + y
        self.dispatch('mouse_press', x, self.height - y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.dispatch('mouse_release', x, self.height - y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.dispatch('mouse_drag', x, self.height - y, dx, -dy, button, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            self.zoom += 0.025
        elif scroll_y < 0:
            self.zoom -= 0.025
        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom
        elif self.zoom < self.min_zoom:
            self.zoom = self.min_zoom

    def change_view(self, width=None, height=None, camera=None, zoom=None):
        camera = self.camera if camera is None else camera
        width = width if width is not None else self.width
        height = height if height is not None else self.height
        zoom = zoom if zoom is not None else self.zoom
        left = camera[0]
        top = camera[1]
        right = camera[0] + width
        bottom = camera[1] + height
        left = left * zoom
        top = top * zoom
        right = right * zoom
        bottom = bottom * zoom
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(left, right, top, bottom, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)


class BirchGame:

    camera_speed = 16

    def __init__(self, asset_dir):
        pyglet.options['debug_gl'] = False
        self.main_batch = pyglet.graphics.Batch()
        self.size = 1280, 720
        self.asset_dir = asset_dir
        md_paths = filter(lambda fn: fn.endswith('.json'), os.listdir(asset_dir))
        self.textures = TextureStore(asset_dir, md_paths)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.ui_elements = []
        self.window = BirchWindow([], self.main_batch, self.ui_elements,
                width=self.size[0], height=self.size[1])
        self.engine = Engine({
            "cells": [],
            "money": 10000,
            "population": 0,
            "speed": 1
            }, self.textures)
        self.mouse_buttons = []
        self.scroll_speed = [2, 2]
        self.camera = [
            int(self.window.width / 2 - CHUNK_SIZE / 2),
            int(self.window.height / 2 - CHUNK_SIZE / 2)
            ]
        self.last_camera = [-1000000, -1000000]
        self.cursor_speed = 8
        self.fps = 100.0
        self.sleeptime = 1 / self.fps
        self.time_spent = 0
        self.kf_rate = 20
        self.kf_countdown = 20
        self.speed_delay = 0.1
        self.edge_delay = 0.5
        self.scroll_pos = 0, 0
        self.jsonenc = ObjectEncoder()
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)
        self.first = True
        self.window.handle('mouse_motion', self.handle_mouse)
        #self.window.handle('resize', self.handle_resize)
        self.window.handle('mouse_press', self.handle_mouse_press)
        self.window.handle('mouse_release', self.handle_mouse_release)
        self.window.handle('mouse_drag', self.handle_mouse_drag)
        self.window.handle('draw', self.handle_draw)
        self.mouse = 0, 0
        self.set_cursor_size(32)
        factor_w = int(self.camera_rect.width / CHUNK_SIZE) * 2
        factor_h = int(self.camera_rect.height / CHUNK_SIZE) * 2
        self.chonk = (
            int(math.ceil(self.camera_rect.width / factor_w)),
            int(math.ceil(self.camera_rect.height / factor_h))
            )
        self.mouse_handlers = []
        self.mouse_press_handlers = []
        self.seed_handlers = []
        self.map_click_handlers = []
        self.camera_controlled = False
        self.player_controlled = False
        self.player = None

    def set_caption(self, *args, **kwargs):
        return self.window.set_caption(*args, **kwargs)

    def set_icon(self, *args, **kwargs):
        return self.window.set_icon(*args, **kwargs)

    def set_player(self, texture_prefix, name='player', position=[0, 0], size=None):
        self.player = Player(name, self.textures, position, texture_prefix,
            batch=None, size=size)
        self.engine.set_cell(self.player)

    def register_mouse_handler(self, handler):
        self.mouse_handlers.append(handler)

    def register_mouse_press_handler(self, handler):
        self.mouse_press_handlers.append(handler)

    def register_map_click_handler(self, handler):
        self.map_click_handlers.append(handler)

    def register_seed_handler(self, handler):
        self.engine.seed_handlers.append(handler)

    def register_tick_handler(self, handler):
        return self.engine.register_tick_handler(handler)

    def run(self):
        pyglet.clock.schedule_interval(self.update, self.sleeptime)
        pyglet.app.run()

    def set_cursor_size(self, size):
        if self.window.cursor is None or size != self.window.cursor.width:
            self.window.cursor = Cursor(*self.mouse, size, self.window.height, batch=self.main_batch)

    def set_cursor_pos(self):
        x, y = self.mouse
        self.window.cursor.x = self.camera[0] + x
        self.window.cursor.y = self.camera[1] + self.window.height - y
        x, y = self.window.cursor.position
        x = x - x % 16
        y = y - y % 16
        self.window.cursor.x = x
        self.window.cursor.y = y
        self.window.cursor.fix_pos(self.camera)

    def handle_draw(self, window):
        pass
        #self.engine.world.draw_chunks(*self.camera, self.camera_rect.width,
        #    self.camera_rect.height)

    def handle_mouse(self, x, y, dx, dy):
        self.mouse = x, y
        hovered = False
        for el in self.ui_elements:
            if el.check_mouse(self.mouse, self.mouse_buttons):
                hovered = True
                self.window.cursor.x = -10000
                self.window.cursor.y = -10000
                break
        if not hovered:
            self.set_cursor_pos()
        for handler in self.mouse_handlers:
            handler(x, y, dx, dy)
        self.window.set_mouse_visible(hovered)

    def handle_mouse_press(self, x, y, button, modifiers):
        self.mouse = x, y
        self.mouse_buttons = set(list(self.mouse_buttons) + [button])
        ui_clicked = False
        self.set_cursor_pos()
        if len(self.mouse_buttons) > 0:
            for el in self.ui_elements:
                ui_clicked = el.check_mouse(self.mouse, self.mouse_buttons) or ui_clicked
        if not ui_clicked:
            # click map
            tool_pos = self.window.cursor.position
            for handler in self.map_click_handlers:
                handler(*tool_pos)
            self.window.set_mouse_visible(False)
        else:
            self.window.set_mouse_visible(True)
        self.set_cursor_pos()
        for handler in self.mouse_press_handlers:
            handler(x, y, button, modifiers)

    def handle_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.handle_mouse_press(x, y, button, modifiers)

    def handle_mouse_release(self, x, y, button, modifiers):
        self.mouse = x, y
        self.mouse_buttons = set(filter(lambda b: b != button, self.mouse_buttons))
        self.set_cursor_pos()

    @property
    def camera_rect(self):
        return Rect(self.camera[0], self.camera[1], self.size[0], self.size[1])

    def centered(self, position):
        return [
            position[0] - int(self.camera_rect.width / 2),
            position[1] - int(self.camera_rect.height / 2)
            ]

    def update(self, dt):
        self.kf_countdown -= 1
        self.engine.tick(dt, checkrect=self.camera_rect)
        if self.camera_controlled:
            if self.keys[key.LEFT]:
                self.camera[0] -= self.camera_speed
            if self.keys[key.RIGHT]:
                self.camera[0] += self.camera_speed
            if self.keys[key.UP]:
                self.camera[1] += self.camera_speed
            if self.keys[key.DOWN]:
                self.camera[1] -= self.camera_speed
        if self.player is not None:
            if self.player_controlled:
                if self.keys[key.A]:
                    self.player.go_left()
                if self.keys[key.D]:
                    self.player.go_right()
                if self.keys[key.W]:
                    self.player.go_up()
                if self.keys[key.S]:
                    self.player.go_down()
            self.player.apply_movement()
            self.camera = self.centered(list(self.player.position))
        delta = abs(self.camera[0] - self.last_camera[0]) + \
                abs(self.camera[1] - self.last_camera[1])
        if delta > self.camera_speed * 2 or not self.first or self.kf_countdown == 0:
            self.window.batches = self.engine.get_batches(*self.camera,
                    self.camera_rect.width, self.camera_rect.height)
            self.last_camera = list(self.camera)
            self.first = True
            inflatefactor = CHUNK_SIZE * 2
            crect = self.camera_rect.inflate(inflatefactor, inflatefactor)
            xes = range(int(crect.left), int(crect.right), self.chonk[0])
            yes = range(int(crect.top), int(crect.bottom), self.chonk[1])
            for point in [[_x, _y] for _y in yes for _x in xes]:
                self.engine.seed(*point)
        self.window.camera = self.camera
        if self.kf_countdown == 0:
            self.kf_countdown = self.kf_rate

