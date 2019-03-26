from pyglet.graphics import vertex_list
from pyglet.gl import GL_QUADS
from birch.ui_element import UIElement
from birch.util import fix_origin

class Cursor(UIElement):

    def __init__(self, x, y, width, window_height):
        super().__init__(x, y, window_height)
        self.width = width
        self.height = width
        self.line_width = 2
        self.init_box()

    @property
    def position(self):
        return self.x, self.y

    def fix_pos(self):
        sharts = self.vx_pos()
        for i, b in enumerate(self.box_vx):
            for z, vx in enumerate(b.vertices):
                if vx != sharts[i][z]:
                    b.vertices[z] = sharts[i][z]

    def vx_pos(self):
        w = self.width
        h = self.height
        x = self.x
        y = self.y
        lw = self.line_width

        sets = (
            ( # 1
                x - lw, y - lw,
                x - lw, y,
                x + w + lw, y,
                x + w + lw, y - lw
            ),
            ( # 2
                x - lw, y,
                x - lw, y + h,
                x, y + h,
                x, y
            ),
            ( # 3
                x + w, y,
                x + w, y + h,
                x + w + lw, y + h + lw,
                x + w + lw, y
            ),
            ( # 4
                x - lw, y + h,
                x - lw, y + h + lw,
                x + w + lw, y + h + lw,
                x + w + lw, y + h
            )
            )
        return sets

    def init_box(self):
        w = self.width
        h = self.height
        x = self.x
        y = self.y
        lw = self.line_width

        sets = self.vx_pos()

        for s in sets:
            self.box_vx.append(vertex_list(4,
                ('v2i', fix_origin(s, self.window_height)),
                ('c3B', (0, 0, 0) * 4)
                ))
            self.box_modes.append(GL_QUADS)

    def draw(self):
        self.draw_box()
