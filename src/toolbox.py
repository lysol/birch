from pygame import draw, Rect, Surface
from util import FG_COLOR, BG_COLOR
import math

class Toolbox:

    position = 20, 20
    padding = 4
    icon_spacing = 4
    width = 77
    height = 300

    def __init__(self, tools, textures):
        self.tools = tools
        self.tool_rects = []
        self.selected = 0
        self.textures = textures
        self.surface = Surface(self.get_rect()[2:])
        # build areas for tools
        for i, tool in enumerate(self.tools):
            tex = self.textures[tool]
            size = tex.get_size()
            if i == 0:
                left = self.padding
                top = self.padding
            else:
                prev_rect = self.tool_rects[i - 1]
                top = prev_rect.top
                left = self.icon_spacing + prev_rect.left + prev_rect.width
                if left + size[0] > self.width - self.icon_spacing:
                    left = self.padding
                    top = prev_rect.top + prev_rect.height + self.icon_spacing
            r = Rect(left, top, size[0], size[1])
            self.tool_rects.append(r)

    def get_rect(self):
        bounds = (
            self.position[0], self.position[1],
            self.width,
            self.height
            )
        return bounds

    def in_bounds(self, pos):
        bounds = self.get_rect()
        return pos[0] >= bounds[0] and pos[0] <= bounds[0] + bounds[2] and \
            pos[1] >= bounds[1] and pos[1] <= bounds[1] + bounds[3]

    def hover_icon(self, pos):
        p = [
            pos[0] - self.position[0],
            pos[1] - self.position[1]
            ]
        for i, rect in enumerate(self.tool_rects):
            if rect.collidepoint(p):
                return i
        return None

    def draw(self, screen):
        bounds = list(self.get_rect())
        bounds[0] = 0
        bounds[1] = 0
        self.surface.fill(FG_COLOR)
        draw.rect(self.surface, BG_COLOR, Rect(*bounds))
        draw.rect(self.surface, FG_COLOR, Rect(0, 0, bounds[2] - 1, bounds[3] - 1), 2)

        for i, tool in enumerate(self.tools):
            self.surface.blit(self.textures[tool], self.tool_rects[i])
            if i == self.selected:
                self.surface.blit(self.textures["cursor_32"], self.tool_rects[i])
        return screen.blit(self.surface, self.position)
