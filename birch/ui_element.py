from pyglet.graphics import Batch, vertex_list, OrderedGroup
from pyglet.gl import GL_QUADS
from birch.util import fix_origin

class UIElement:

    width = 100
    height = 100
    line_width = 2

    def __init__(self, x, y, window_height, batch=None):
        self.x = x
        self.y = y
        self.batch = Batch() if batch is None else batch
        self.click_regions = {}
        self.click_handlers = {}
        self.ui_elements = []
        self.box_vx = []
        self.box_modes = []
        self.window_height = window_height
        self.groupNumber = 100
        if len(self.box_vx) == 0:
            self.init_box()

    def init_box(self):
        w = self.width
        h = self.height
        pos = self.x, self.y

        bgvx = fix_origin((
            pos[0], pos[1],
            pos[0], pos[1] + h,
            pos[0] + w, pos[1] + h,
            pos[0] + w, pos[1]
            ), self.window_height)
        bgvx2 = (
            bgvx[0] + 2, bgvx[1] - 2,
            bgvx[2] + 2, bgvx[3] + 2,
            bgvx[4] - 2, bgvx[5] + 2,
            bgvx[6] - 2, bgvx[7] - 2
            )
        self.box_vx.append(self.batch.add(4,
            GL_QUADS,
            OrderedGroup(self.groupNumber),
            ('v2i', bgvx),
            ('c3B', (0, 0, 0) * 4)
            ))

        self.box_vx.append(self.batch.add(4,
            GL_QUADS,
            OrderedGroup(self.groupNumber),
            ('v2i', bgvx2),
            ('c3B', (255, 255, 255) * 4)
            ))

    def handle_region(self, name, handler, x, y, w, h):
        self.click_regions[name] = (x, y, w, h)
        self.click_handlers[name] = handler

    def hover(self, pos):
        return True

    def in_region(self, x, y, rx, ry, rw, rh):
        return x >= rx and x <= rx + rw and \
            y >= ry and y <= ry + rh

    def check_mouse(self, pos, buttons):
        something = False
        if len(buttons) == 0:
            # nothing clicked, hover
            if self.in_region(*pos, self.x, self.y, self.width, self.height):
                something = self.hover(pos)
        else:
            for region in self.click_regions:
                r = self.click_regions[region]
                args = list(pos)
                args.extend(r)
                if self.in_region(*args):
                    self.click_handlers[region](region, *pos, buttons)
                    something = True
        for el in self.ui_elements:
            something = el.check_mouse(pos, buttons) or something
        return something



