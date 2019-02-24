from pygame import draw, Rect, Surface
from pygame.font import Font
import math

WHITE = 255, 255, 255
BLACK = 0, 0, 0

class Statusbox:

    position = 92, 20
    dimensions = 688, 32
    padding = 4

    def __init__(self, textures, engine):
        self.textures = textures
        print(self.get_bounds())
        self.surface = Surface(self.get_bounds()[2:])
        self.font = Font(None, 24)
        self.engine = engine

    def get_bounds(self):
        return (
            self.position[0],
            self.position[1],
            self.dimensions[0],
            self.dimensions[1]
            )

    def in_bounds(self, pos):
        bounds = self.get_bounds()
        return pos[0] >= bounds[0] and pos[0] <= bounds[0] + bounds[2] and \
            pos[1] >= bounds[1] and pos[1] <= bounds[1] + bounds[3]

    def draw(self, screen):
        bounds = list(self.get_bounds())
        bounds[0] = 0
        bounds[1] = 0
        draw.rect(self.surface, WHITE, Rect(*bounds))
        draw.rect(self.surface, BLACK, Rect(*bounds), 2)
        message = "$%d   Population: %d" % (self.engine.state["money"], self.engine.state["population"])
        text = self.font.render(message, 1, BLACK)
        self.surface.blit(text, (3, 3))
        screen.blit(self.surface, self.position)