from os import unlink
from random import choice, randint, random, shuffle
from math import sin, pi, hypot
from collections import deque
from uuid import uuid4
from datetime import datetime, timedelta
from pyglet.gl import *
from pyglet import resource
from pyglet.sprite import Sprite
from pyglet.image import Texture, ImageData
import pyglet
from PIL import Image, ImageDraw
from birch.cells.rci import RCell, CCell, ICell
from birch.cells.cell import Cell
from birch.cells.blueprint import BlueprintCell
from birch.cells.connectable import ConnectableCell
from birch.cells.road import RoadCell
from birch.cells.rail import RailCell
from birch.cells.water import WaterCell
from birch.cells.brick_halfwall import BrickHalfWallCell
from birch.cells.brick_wall import BrickWallCell
from birch.cells.uranium import Uranium
from birch.cells.tree import PineTree, BirchTree
from birch.util import clamp, pi2, Rect
from birch.world import World

class Engine:
    insert_chunk = 15

    def __init__(self, state, textures):
        self.state = state
        self.ticks = 0
        self.textures = textures
        self.world = World()
        self.deferred_inserts = deque([])
        self.tick_handlers = []
        self.seed_handlers = []

    def in_range(self, camera, pos):
        return pos[0] > camera[0] - 1000 or \
            pos[0] < camera[0] + 1000 or \
            pos[1] < camera[1] - 1000 or \
            pos[1] < camera[1] + 1000

    def register_tick_handler(self, handler):
        self.tick_handlers.append(handler)

    def register_seed_handler(self, handler):
        self.seed_handlers.append(handler)

    def tick(self, dt, checkrect=None):
        damage = False
        self.ticks += self.state["speed"]
        changed = []
        if len(self.deferred_inserts) > 0:
            inserted = self.do_insert()
            checkrect.inflate_in_place(checkrect.width, checkrect.height)
            if checkrect is not None:
                for item in inserted:
                    if checkrect.colliderect(item.rect):
                        changed.append(item)
            else:
                changed.extend(inserted)
        for cell in self.state["cells"]:
            if cell.next_update != -1 and self.ticks >= cell.next_update:
                cell.update(self.ticks, self)
        for handler in self.tick_handlers:
            handler(self, dt, self.ticks)
        return changed

    def get_cell(self, x, y, w, h):
        return self.world.get(x, y, w, h)

    def do_insert(self):
        cells = []
        for z in range(self.insert_chunk):
            if len(self.deferred_inserts) == 0:
                break
            bp = self.deferred_inserts.popleft()
            cells.append(bp.to_cell())
        if len(cells) > 0:
            self.state['cells'].extend(cells)
            for cell in cells:
                self.world.insert(cell, *cell.position)
                self.texture_check(cell)
        return cells

    def set_cell(self, cell, alias=True, grow=True, defer=False):
        if alias:
            apos = self.alias_pos(cell.left, cell.top)
            cell.position = apos[0], apos[1]
        if defer:
            self.deferred_inserts.append(cell)
        else:
            self.state['cells'].append(cell)
            self.world.insert(cell, *cell.position)
            self.texture_check(cell)

    def texture_check(self, cell):
        if issubclass(type(cell), ConnectableCell):
            newbounds = cell.rect.inflate(cell.width * 4, cell.height * 4).bounds
            innerrect = cell.rect.inflate(cell.width * 2, cell.height * 2)
            surrounding = self.world.get(*newbounds)
            for other in surrounding:
                if type(other) == type(cell) and other.rect.colliderect(innerrect):
                    other.cache_texture(surrounding)

    def del_cell(self, cell):
        self.world.delete(cell, *cell.position)
        if cell in self.state['cells']:
            self.state['cells'].remove(cell)

    def alias_pos(self, x, y, size=16):
        return [
            x - x % size,
            y - y % size
            ]

    def get_batches(self, x, y, w=1, h=1):
        r = Rect(x, y, w, h)
        r.inflate_in_place(w, h)
        return self.world.get_batches(*r.topleft, r.width, r.height)

    def seed(self, x, y):
        if not self.world.unseeded(x, y):
            return
        tl = self.world._alias(x, y)
        ax, ay = tuple(map(lambda z: z * self.world.chunk_size, tl))
        for handler in self.seed_handlers:
            cells = handler(self, Rect(ax, ay, self.world.chunk_size, self.world.chunk_size))
            self.deferred_inserts.extend(cells)

        self.world.seed(*tl, [])
        return True
