import math
from pyglet.sprite import Sprite
from pyglet.graphics import draw
from pyglet import gl
from birch.util import FG_COLOR, BG_COLOR, Rect, fix_origin
from birch.ui_element import UIElement

class Statusbox(UIElement):

    speeds = "pause", "slow", "normal", "fast"
    speed_icon_dims = 24, 22

    width = 682
    height = 34

    padding = 4

    def __init__(self, window_height, textures, engine):
        super().__init__(100, 20, window_height)
        self.textures = textures
        self.engine = engine
        self.rect = Rect(
            self.x,
            self.y,
            self.width,
            self.height
            )
        self.speed_sprites = {}
        sid = self.speed_icon_dims
        _sp_pos = (
            self.x + self.width - sid[0] - 6,
            self.window_height - (self.y + self.padding + 4 + sid[1]))

        for speed in self.speeds:
            self.speed_sprites[speed] = Sprite(self.textures[speed],
                _sp_pos[0], _sp_pos[1], batch=self.batch)
            self.speed_sprites[speed].scale = 2

        self.speed_icon_rect = Rect(
            _sp_pos[0] + self.x, _sp_pos[1] + self.y,
            32, 32)

    def in_bounds(self, pos):
        return self.rect.collidepoint(pos)

    def speed_icon_hover(self, pos):
        return self.speed_icon_rect.collidepoint(pos)

    def draw(self):
        speed = self.engine.state['speed']
        self.draw_box()
        self.speed_sprites[self.speeds[speed]].draw()

