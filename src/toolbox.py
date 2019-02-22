from pygame import draw, Rect
import math

WHITE = 255, 255, 255
BLACK = 0, 0, 0

class Toolbox:

    position = 20, 20
    padding = 4
    icon_spacing = 36

    def __init__(self, tools, textures):
        self.tools = tools
        self.selected = 0
        self.textures = textures

    def get_bounds(self):
        bounds = (
            self.position[0], self.position[1],
            self.padding + self.icon_spacing * 2,
            self.padding + math.ceil(len(self.tools) / 2.0) * self.icon_spacing)
        return bounds

    def in_bounds(self, pos):
        bounds = self.get_bounds()
        return pos[0] >= bounds[0] and pos[0] <= bounds[0] + bounds[2] and \
            pos[1] >= bounds[1] and pos[1] <= bounds[1] + bounds[3]

    def hover_icon(self, pos):
        x = math.floor((pos[0] - self.padding - self.position[0]) / self.icon_spacing)
        y = math.floor((pos[1] - self.padding - self.position[1]) / self.icon_spacing)
        return x + y * 2

    def draw(self, screen):
        bounds = self.get_bounds()
        draw.rect(screen, WHITE, Rect(*bounds))
        draw.rect(screen, BLACK, Rect(*bounds), 2)

        for i, tool in enumerate(self.tools):
            icon_position = (
                (i % 2 * self.icon_spacing) + self.position[0] + self.padding,
                math.floor(i / 2.0) * self.icon_spacing + self.position[1] + self.padding
                )
            screen.blit(self.textures[tool], icon_position)
            if i == self.selected:
                screen.blit(self.textures["cursor"], icon_position)
