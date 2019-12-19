import json
import sys
import os
from birch.cells.blueprint import BlueprintCell
from pyglet.graphics import Batch



class Scene:
    def __init__(self, name, blueprint=[[[]]]):
        self.name = name
        self.blueprint = blueprint
        self.cells = []
        self.spawned = False
        for row in self.blueprint:
            self.cells.append([])
            for col in row:
                self.cells[-1].append([])
        self.batch = Batch()

    def spawn(self, engine):
        for y, row in enumerate(self.blueprint):
            for x, cell in enumerate(row):
                if y % 128 == 0 and x % 128 == 0:
                    print('Working on spawning %d, %d' % (x, y), len(cell))
                for bp in cell:
                    bp.update((engine.textures, bp.args[1]))
                    bp.to_cell()
                    bp.batch = self.batch
                    self.cells[y][x].append(bp)
        self.spawned = True

"""
implements a world class that can
* select different scenes/maps
* use data from the Tiled map editor
"""
class TiledWorld:
    def __init__(self, mapfiles, celldict):
        # maps are the blueprints that scenes are generated from
        self.maps = {}
        # scenes are instances of maps
        self.scenes = {}
        self.active_scene = None

        self.celldict = celldict
        for mapfile in mapfiles:
            token = os.path.basename(mapfile)
            self.maps[token] = self.load_map(mapfile)
            self.scenes[token] = Scene(token, self.maps[token])
            if self.active_scene is None:
                self.active_scene = token

    @property
    def scene(self):
        return self.scenes[self.active_scene]

    def set_engine(self, engine):
        self.engine = engine

    def spawn_maps(self):
        for token in self.scenes:
            self.scenes[token].spawn(self.engine)

    def load_map(self, map_filename):
        print('loading', map_filename)
        fh = open(map_filename, 'r')
        contents = fh.read()
        mapdata = json.loads(contents)
        tiles = {}
        tilecounter = 0
        loadcells = []
        for y in range(mapdata['height']):
            loadcells.append([])
            for x in range(mapdata['height']):
                loadcells[-1].append([])
        for tileset in mapdata['tilesets']:
            for tile in tileset['tiles']:
                found = False
                for prop in tile['properties']:
                    if prop['name'] == 'name':
                        tiles[tile['id']] = prop['value']
                        break
        print('tiles', tiles)
        for layer in mapdata['layers']:
            curse = 0
            x = 0
            y = 0
            while curse < len(layer['data']):
                x = curse % mapdata['height']
                y = int(curse / mapdata['height'])
                if layer['data'][curse] != 0:
                    tileindex = layer['data'][curse] - 1
                    cls = tiles[tileindex]
                    # none will be replaced with the engine.textures object later
                    loadcells[y][x].append(BlueprintCell(self.celldict[cls], (None, (x, y))))
                curse += 1
                if curse % 1024 == 0:
                    print('curse is %d (%d %d)' % (curse, x, y))
        return loadcells

    def insert(self, cell, x, y):
        self.scene.cells[y][x].append(cell)

    def get(self, tlx, tly, w, h):
        x = tlx
        y = tly
        out = []
        while y < tly + h:
            while x < tlx + w:
                out.extend(self.scene.cells[y][x])
            x += 1
        y += 1

    def delete(self, cell, x, y):
        self.scene.cells[y][x] = filter(lambda cell: cell != cell, self.scene.cells[y][x])

    def get_batches(self, tlx, tly, w, h):
        return [self.scene.batch]

    def unseeded(self, x, y):
        return False

    def _alias(self, x, y):
        pass

    def seed(self, x, y, cells):
        pass

