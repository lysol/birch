from pygame import draw, Rect, Surface
from pygame.font import Font
from util import FG_COLOR, BG_COLOR
import math

class Statusbox:

    speeds = "pause", "slow", "normal", "fast"
    speed_icon_dims = 24, 22

    position = 100, 20
    dimensions = 682, 32
    padding = 4

    def __init__(self, textures, engine):
        self.textures = textures
        print(self.get_bounds())
        self.surface = Surface(self.get_bounds()[2:])
        self.font = Font(None, 24)
        self.engine = engine
        self.bounds = Rect(
            self.position[0],
            self.position[1],
            self.dimensions[0],
            self.dimensions[1]
            )

    def in_bounds(self, pos):
        return self.bounds.collidepoint(pos)

    @property
    def speed_icon_position(self):
        return (
            self.dimensions[0] - self.speed_icon_dims[0] - 6,
            self.dimensions[1] - self.speed_icon_dims[1] - \
                (self.dimensions[1] - self.speed_icon_dims[1]) / 2)

    @property
    def speed_icon_rect(self):
        return Rect(
            self.speed_icon_position[0] + self.position[0],
            self.speed_icon_position[1] + self.position[1],
            self.speed_icon_dims[0],
            self.speed_icon_dims[1]
            )

    def speed_icon_hover(self, pos):
        return self.speed_icon_rect.collidepoint(pos)

    def get_bounds(self):
        return (
            self.position[0],
            self.position[1],
            self.dimensions[0],
            self.dimensions[1]
            )

    def draw(self, screen, speed):
        bounds = list(self.get_bounds())
        bounds[0] = 0
        bounds[1] = 0
        draw.rect(self.surface, BG_COLOR, Rect(*bounds))
        draw.rect(self.surface, FG_COLOR, Rect(0, 0, bounds[2] - 1, bounds[3] - 1), 2)
        message = "$%d   Population: %d" % (self.engine.state["money"], self.engine.state["population"])
        text = self.font.render(message, 1, FG_COLOR)
        self.surface.blit(text, (3, 3))
        self.surface.blit(self.textures[self.speeds[speed]], (
            self.dimensions[0] - self.speed_icon_dims[0] - 6,
            self.dimensions[1] - self.speed_icon_dims[1] - \
                (self.dimensions[1] - self.speed_icon_dims[1]) / 2)
                )
        return screen.blit(self.surface, self.position)
