import math
import pyglet
from pyglet.graphics import OrderedGroup
from birch.util import FG_COLOR, BG_COLOR, fix_origin, Rect
from birch.ui_element import UIElement
from birch.cursor import Cursor

class Toolbox(UIElement):

    padding = 8
    icon_spacing = 4
    height = 300

    tools = (
        "bulldoze",
        "r_0_0",
        "c_0_0",
        "i_0_0",
        "road_h_0",
        "rail_h",
        "water_o_0"
        )

    def __init__(self, window_height, textures, batch=None):
        self.width = self.padding * 2 + self.icon_spacing + 64
        super().__init__(20, 20, window_height, batch=batch)
        self.sprites = []
        self.tool_rects = []
        self.selected = None
        self.textures = textures
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
                if left + size[0] > self.x + self.width + self.icon_spacing:
                    left = self.padding + self.x
                    top = prev_rect.bottom + self.icon_spacing
            self.handle_region(tool, self.set_tool, left, top, tex.width * 2, tex.height * 2)
            np = fix_origin((left, top + tex.height * 2), self.window_height)
            self.sprites.append(pyglet.sprite.Sprite(
                self.textures[tool], np[0], np[1], batch=self.batch, group=OrderedGroup(self.groupNumber + 1)))
            self.tool_indexes[tool] = i
            self.sprites[-1].scale = 2
            r = Rect(left, top, size[0], size[1])
            self.tool_rects.append(r)

    @property
    def active_sprite(self):
        return self.sprite_by_name(self.selected)

    def sprite_by_name(self, tool):
        return self.sprites[self.tool_indexes[tool]]

    def set_tool(self, tool, x=None, y=None, buttons=None):
        self.selected = tool
        tool_sprite = self.sprite_by_name(tool)
        self.ui_elements = [Cursor(tool_sprite.x, tool_sprite.y,
            self.textures[tool].width * 2, self.window_height)]
        self.ui_elements[0].fix_pos((0, 0))

    @property
    def tool_size(self):
        if self.selected == 'bulldoze':
            return 16
        return self.click_regions[self.selected][2]
