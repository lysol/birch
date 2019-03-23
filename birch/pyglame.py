import pyglet, json
from pyglet.window import key
from pyglet.gl import *
from birch.texture_store import TextureStore
from birch.toolbox import Toolbox
#from birch.statusbox import Statusbox
#from birch.rcibox import RCIbox
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

    def __init__(self, batches, ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batches = batches
        self.ui = ui
        self.handlers = {}
        self.camera = (0, 0)
        self.zoom = 1
        self.reference_point = 0, 0
        self.cursor_sprite = None

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
        if self.cursor_sprite is not None:
            self.cursor_sprite.draw()
        for y in range(0, self.height, 64):
            for x in range(0, self.width, 64):
                delto = x, y
                color = (255, 0, 0) if delto[0] % 128 == 0 and delto[1] % 128 == 0 else (0, 255, 0)
                if delto[0] == 0 and delto[1] == 0:
                    color = (255, 255, 0)
                self.draw_dot(x, y, color)
        self.change_view(zoom=1.0, camera=(0, 0))
        for el in self.ui:
            el.draw()

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
        self.engine = Engine({
            "cells": [],
            "money": 10000,
            "population": 0,
            "speed": 1
            }, self.textures)
        self.mouse_buttons = []
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
        self.window.handle('mouse_motion', self.handle_mouse)
        #self.window.handle('resize', self.handle_resize)
        self.window.handle('mouse_press', self.handle_mouse_press)
        self.window.handle('mouse_release', self.handle_mouse_release)
        self.window.handle('mouse_drag', self.handle_mouse_drag)
        self.mouse = 0, 0
        self.init_ui()
        self.set_sprite_cursor()

    def init_ui(self):
        self.toolbox = Toolbox(self.window.height, self.textures)
        self.ui_elements.append(self.toolbox)
        self.toolbox.set_tool('bulldoze')

    def run(self):
        self.engine.seed(0, 0)
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()
        #self.init_panels()

    def set_sprite_cursor(self):
        if self.toolbox.use_sprite_cursor:
            tex = self.toolbox.selected
        else:
            tex = 'cursor_%d' % self.toolbox.tool_size
        self.window.cursor_sprite = pyglet.sprite.Sprite(self.textures[tex], *self.mouse)
        self.window.cursor_sprite.scale = 2

    def set_cursor_sprite_pos(self):
        x, y = self.mouse
        self.window.cursor_sprite.x = self.camera[0] + x
        self.window.cursor_sprite.y = self.camera[1] + self.window.height - y
        x, y = self.window.cursor_sprite.position
        x = x - x % 16
        y = y - y % 16
        self.window.cursor_sprite.x = x
        self.window.cursor_sprite.y = y

    def handle_mouse(self, x, y, dx, dy):
        self.mouse = x, y
        hovered = False
        for el in self.ui_elements:
            if el.check_mouse(self.mouse, self.mouse_buttons):
                hovered = True
                self.window.cursor_sprite.x = -10000
                self.window.cursor_sprite.y = -10000
                break
        if not hovered:
            self.set_cursor_sprite_pos()
        self.window.set_mouse_visible(hovered)

    def handle_mouse_press(self, x, y, button, modifiers):
        self.mouse = x, y
        self.mouse_buttons = set(list(self.mouse_buttons) + [button])
        ui_clicked = False
        self.set_sprite_cursor()
        self.set_cursor_sprite_pos()
        if len(self.mouse_buttons) > 0:
            for el in self.ui_elements:
                ui_clicked = el.check_mouse(self.mouse, self.mouse_buttons) or ui_clicked
        if not ui_clicked:
            # click map
            tool_pos = self.window.cursor_sprite.position
            self.engine.use_tool(self.toolbox.selected, tool_pos[0], tool_pos[1],
                tool_size=self.toolbox.tool_size)
            self.window.set_mouse_visible(False)
        else:
            self.window.set_mouse_visible(True)
        self.set_sprite_cursor()
        self.set_cursor_sprite_pos()

    def handle_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse = x, y
        self.set_cursor_sprite_pos()

    def handle_mouse_release(self, x, y, button, modifiers):
        self.mouse = x, y
        self.mouse_buttons = set(filter(lambda b: b != button, self.mouse_buttons))
        self.set_cursor_sprite_pos()

    @property
    def camera_rect(self):
        return Rect(self.camera[0], self.camera[1], self.size[0], self.size[1])

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

