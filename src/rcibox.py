from pygame import draw, Rect, Surface
from pygame.font import Font
import math

WHITE = 255, 255, 255
BLACK = 0, 0, 0

class RCIbox:

    dimensions = 72, 36
    bar_width = 4
    padding = 2

    def __init__(self):
        self.surface = Surface(self._dims_padded)
        self.font = Font(None, 16)

    def _bar_width(self, v, maxw):
        maxbar = self.dimensions[0] - 4 - maxw - self.padding * 2
        return max(0, math.floor(maxbar * v))

    @property
    def _dims_padded(self):
        return list(map(lambda x: x + self.padding * 2, self.dimensions))

    def draw(self, screen, r, c, i):
        vals = [r, c, i]
        padding = self.padding
        dims = self.dimensions
        dims_padded = self._dims_padded
        draw.rect(self.surface, WHITE, Rect(0, 0, *dims_padded))
        draw.rect(self.surface, BLACK, Rect(0, 0, dims_padded[0] - 1, dims_padded[1] - 1), 2)

        rtext = self.font.render("R", 1, BLACK)
        ctext = self.font.render("C", 1, BLACK)
        itext = self.font.render("I", 1, BLACK)
        widths = []
        heights = []
        widths.append(rtext.get_width())
        widths.append(ctext.get_width())
        widths.append(itext.get_width())
        heights.append(rtext.get_height())
        heights.append(ctext.get_height())
        heights.append(itext.get_height())
        maxw = max(widths)
        maxh = max(heights)

        bars = [
            int(self._bar_width(r, maxw)),
            int(self._bar_width(c, maxw)),
            int(self._bar_width(i, maxw))
            ]

        half = (self.dimensions[0] - 4 - maxw) / 2
        draw.line(self.surface,
                BLACK,
                (maxw + 2 + padding + half, 0),
                (maxw + 2 + padding + half, 2 + maxh * 3))

        self.surface.blit(rtext, (padding + 2, padding + 2))
        draw.rect(self.surface, BLACK, Rect(padding + 4 + maxw, padding + 1,
            bars[0], maxh - 2))
        self.surface.blit(ctext, (padding + 2, padding + 2 + maxh - 1))
        draw.rect(self.surface, BLACK, Rect(padding + 4 + maxw, padding + 1 + maxh,
            bars[1], maxh - 2))
        self.surface.blit(itext, (padding + 2, padding + 2 + maxh * 2 - 2))
        draw.rect(self.surface, BLACK, Rect(padding + 4 + maxw, padding + 1 + maxh * 2,
            bars[2], maxh - 2))
        screen.blit(self.surface, (padding + 4, screen.get_size()[1] - padding - self.dimensions[1] - 4))
