import json
import sys
import os
from birch.cells.blueprint import BlueprintCell
from birch.cells.tiled_cell import TiledCell
from birch.util import Rect
from pyglet.graphics import Batch

class Scene:
    def __init__(self, name, blueprint=[[[]]], tile_size=32):
        self.name = name
        self.blueprint = blueprint
        self.cells = []
        self.spawned = False
        self.tile_size = tile_size
        for row in self.blueprint:
            self.cells.append([])
            for col in row:
                self.cells[-1].append([])
        self.batch = Batch()

    def spawn(self, engine):
        for y, row in enumerate(self.blueprint):
            for x, cell in enumerate(row):
                for bp in cell:
                    bp.update_arg(1, engine.textures)
                    cell = bp.to_cell()
                    cell.batch = self.batch
                    self.cells[y][x].append(cell)
        self.spawned = True

"""
implements a world class that can
* select different scenes/maps
* use data from the Tiled map editor
"""
class TiledWorld:
    def __init__(self, mapfiles):
        # maps are the blueprints that scenes are generated from
        self.maps = {}
        # scenes are instances of maps
        self.scenes = {}
        self.active_scene = None

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
        tw = mapdata['tilewidth']
        th = mapdata['tileheight']
        tiles = {}
        tile_properties = {}
        tilecounter = 0
        loadcells = []
        for y in range(mapdata['height']):
            loadcells.append([])
            for x in range(mapdata['height']):
                loadcells[-1].append([])
        for tileset in mapdata['tilesets']:
            for tile in tileset['tiles']:
                found = False
                properties = {}
                if 'properties' in tile:
                    for prop in tile['properties']:
                        properties[prop['name']] = prop['value']
                        if prop['name'] == 'name':
                            tiles[tile['id']] = prop['value']
                tile_properties[tile['id']] = properties
                tile_properties[tile['id']]['name'] = os.path.basename(tile['image']).replace('.png','')
        for layer in mapdata['layers']:
            curse = 0
            x = 0
            y = 0
            while curse < len(layer['data']):
                x = curse % mapdata['height']
                y = int(curse / mapdata['height'])
                y = mapdata['height'] - y - 1
                if layer['data'][curse] != 0:
                    tileindex = layer['data'][curse] - 1
                    # none will be replaced with the engine.textures object later
                    loadcells[y][x].append(BlueprintCell(TiledCell, [tile_properties[tileindex], None,
                        (x * tw * 2, y * th * 2)]))
                curse += 1
        return loadcells

    def insert(self, cell, x, y):
        p2tx = int(x / self.scene.tile_size / 2)
        p2ty = int(y / self.scene.tile_size / 2)
        self.scene.cells[p2ty][p2tx].append(cell)
        cell.batch = self.scene.batch

    def get(self, tlx, tly, w, h):
        x = tlx
        y = tly
        out = []
        while y < tly + h:
            while x < tlx + w:
                out.extend(self.scene.cells[y][x])
            x += 1
        y += 1
        return out

    def delete(self, cell, x, y):
        self.scene.cells[int(y / self.scene.tile_size / 2)][int(x / self.scene.tile_size / 2)] = \
            filter(lambda cell: cell != cell, self.scene.cells[y][x])

    def get_batches(self, tlx, tly, w, h):
        return [self.scene.batch]

    def unseeded(self, x, y):
        return False

    def _alias(self, x, y):
        pass

    def seed(self, x, y, cells):
        pass

    def collision_check(self, px, py, pw, ph):
        tl_x = px + 8
        tl_y = py + 8
        tr_x = px + pw - 8
        tr_y = py + 8
        br_x = tr_x
        br_y = py + ph - 8
        bl_x = tl_x
        bl_y = br_y

        point_checks = list(set((
            (int(tl_x / self.scene.tile_size / 2), int(tl_y / self.scene.tile_size / 2)),
            (int(tr_x / self.scene.tile_size / 2), int(tr_y / self.scene.tile_size / 2)),
            (int(br_x / self.scene.tile_size / 2), int(br_y / self.scene.tile_size / 2)),
            (int(bl_x / self.scene.tile_size / 2), int(bl_y / self.scene.tile_size / 2))
        )))
        for pc in point_checks:
            try:
                cells = self.scene.cells[pc[1]][pc[0]]
                for cell in cells:
                    if cell.name != 'player' and hasattr(cell, 'impassible') and \
                        cell.impassible == True:
                        return False
            except IndexError:
                continue
        return True
