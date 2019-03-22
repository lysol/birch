import math
import pyglet
from pygame import Rect
from birch.util import FG_COLOR, BG_COLOR, fix_origin
from birch.ui_element import UIElement

class Toolbox(UIElement):

    padding = 4
    icon_spacing = 4
    width = 77
    height = 300

    tools = (
        "bulldoze",
        "r_0_0",
        "c_0_0",
        "i_0_0",
        "road_h",
        "rail_h"
        )

    def __init__(self, window_height, textures):
        super().__init__(20, 20)
        self.window_height = window_height
        self.batch = pyglet.graphics.Batch()
        self.sprites = []
        self.tool_rects = []
        self.selected = None
        self.textures = textures
        self.cursor_32 = pyglet.sprite.Sprite(self.textures['cursor_32'], -1000, -1000)
        self.cursor_16 = pyglet.sprite.Sprite(self.textures['cursor_16'], -1000, -1000)
        self.cursor_32.scale = 2
        self.cursor_16.scale = 2
        self.active_cursor = self.cursor_32
        self.tool_indexes = {}
        # build areas for tools
        for i, tool in enumerate(self.tools):
            tex = self.textures[tool]
            size = (tex.width * 2, tex.height * 2)
            if i == 0:
                left = self.padding + self.x
                top = self.padding + self.y
            else:
                prev_rect = self.tool_rects[i - 1]
                top = prev_rect.top
                left = prev_rect.right + self.icon_spacing
                if left + size[0] > self.x + self.width - self.icon_spacing:
                    left = self.padding + self.x
                    top = prev_rect.bottom + self.icon_spacing
            self.handle_region(tool, self.set_tool, left, top, tex.width * 2, tex.height * 2)
            np = fix_origin((left, top + tex.height * 2), self.window_height)
            self.sprites.append(pyglet.sprite.Sprite(self.textures[tool], np[0], np[1], batch=self.batch))
            self.tool_indexes[tool] = i
            self.sprites[-1].scale = 2
            r = Rect(left, top, size[0], size[1])
            self.tool_rects.append(r)

    @property
    def use_sprite_cursor(self):
        if self.selected == 'bulldoze':
            return False
        else:
            return True

    @property
    def active_sprite(self):
        return self.sprite_by_name(self.selected)

    def sprite_by_name(self, tool):
        return self.sprites[self.tool_indexes[tool]]

    def set_tool(self, tool, x=None, y=None, buttons=None):
        self.selected = tool
        if self.textures[tool].width == 8:
            self.active_cursor = self.cursor_16
        else:
            self.active_cursor = self.cursor_32
        tool_sprite = self.sprite_by_name(tool)
        self.active_cursor.x = tool_sprite.x
        self.active_cursor.y = tool_sprite.y

    @property
    def tool_size(self):
        if self.selected == 'bulldoze':
            return 16
        return self.click_regions[self.selected][2]

    def draw(self):
        w = self.width
        h = self.height
        pos = self.x, self.y

        bgvx = fix_origin((
            pos[0], pos[1],
            pos[0], pos[1] + h,
            pos[0] + w, pos[1] + h,
            pos[0] + w, pos[1]
            ), self.window_height)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v2i', bgvx),
            ('c3B', (0, 0 ,0) * 4)
        )
        bgvx2 = (
            bgvx[0] + 2, bgvx[1] - 2,
            bgvx[2] + 2, bgvx[3] + 2,
            bgvx[4] - 2, bgvx[5] + 2,
            bgvx[6] - 2, bgvx[7] - 2
            )
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v2i', bgvx2),
            ('c3B', (255, 255, 255) * 4)
        )
        self.batch.draw()
        self.active_cursor.draw()
