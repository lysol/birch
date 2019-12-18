import math
from pyglet.graphics import OrderedGroup
from pyglet.gl import *
from birch.ui_element import UIElement
from birch.util import FG_COLOR, BG_COLOR, Rect, fix_origin

class RCIbox(UIElement):

    height = 38
    bar_width = 4
    padding = 2
    bar_start = 4
    bar_start_left = 10
    bar_height = 8
    bar_spacing = 3

    def __init__(self, x, y, window_height, batch=None, width=None):
        self.width = 72 if width is None else width
        super().__init__(x, y, window_height, batch=batch)
        self.rect = Rect(x, y, self.width, self.height)
        self._r = 0
        self._c = 0
        self._i = 0
        self.bar_vx_index_start = 2

    @property
    def r(self):
        return self._r

    @property
    def c(self):
        return self._c

    @property
    def i(self):
        return self._i

    @r.setter
    def r(self, val):
        val = round(val, 2)
        if val != self._r:
            self._r = val
            self._set_bar_width(0, val)

    @c.setter
    def c(self, val):
        val = round(val, 2)
        if val != self._c:
            self._c = val
            self._set_bar_width(1, val)

    @i.setter
    def i(self, val):
        val = round(val, 2)
        if val != self._i:
            self._i = val
            self._set_bar_width(2, val)

    def _set_bar_width(self, bar_index, val):
        vx = self.box_vx[self.bar_vx_index_start + bar_index]
        worp = self._bar_width(val, self.width - 18)
        vort = self.x + self.bar_start_left + worp
        vx.vertices[4] = vort
        vx.vertices[6] = vort

    def _bar_width(self, v, maxw):
        return max(0, math.floor(v * maxw))

    @property
    def _dims_padded(self):
        return list(map(lambda x: x + self.padding * 2, self.dimensions))

    def in_bounds(self, pos):
        return self.rect.collidepoint(pos)

    def init_box(self):
        w = self.width
        h = self.height
        pos = self.x, self.y
        group = OrderedGroup(self.groupNumber)

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
            group,
            ('v2i', bgvx),
            ('c3B', (0, 0, 0) * 4)
            ))

        self.box_vx.append(self.batch.add(4,
            GL_QUADS,
            group,
            ('v2i', bgvx2),
            ('c3B', (255, 255, 255) * 4)
            ))
        bar_start = self.bar_start
        bar_height = self.bar_height
        bar_spacing = self.bar_spacing + bar_height
        bar_start_left = self.bar_start_left
        bars = [
            (pos[0] + bar_start_left, pos[1] + bar_start,
             pos[0] + bar_start_left, pos[1] + bar_start + bar_height,
             pos[0] + bar_start_left + 1, pos[1] + bar_start + bar_height,
             pos[0] + bar_start_left + 1, pos[1] + bar_start)
            ]
        bars.append((
            bars[0][0], bars[0][1] + bar_spacing,
            bars[0][2], bars[0][3] + bar_spacing,
            bars[0][4], bars[0][5] + bar_spacing,
            bars[0][6], bars[0][7] + bar_spacing
            ))
        bars.append((
            bars[1][0], bars[1][1] + bar_spacing,
            bars[1][2], bars[1][3] + bar_spacing,
            bars[1][4], bars[1][5] + bar_spacing,
            bars[1][6], bars[1][7] + bar_spacing
            ))
        for bar in bars:
            self.box_vx.append(self.batch.add(4,
                GL_QUADS, group,
                ('v2i', fix_origin(bar, self.window_height)),
                ('c3B', (0, 0, 0) * 4)
                ))

