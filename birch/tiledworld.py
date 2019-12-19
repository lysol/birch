import json
import sys
import os
from birch.cells.blueprint import BlueprintCell

"""
implements a world class that can
* select different scenes/maps
* use data from the Tiled map editor
"""
class TiledWorld:
    def __init__(self, mapfiles, celldict):
        self.maps = {}
        self.active_map = None
        self.celldict = celldict
        for mapfile in mapfiles:
            token = os.path.basename(mapfile)
            self.maps[token] = self.load_map(mapfile)
            if self.active_map is None:
                self.active_map = self.maps[token]
        print(self.maps)

    def load_map(self, map_filename):
        print('loading', map_filename)
        fh = open(map_filename, 'r')
        contents = fh.read()
        mapdata = json.loads(contents)
        tiles = {}
        tilecounter = 0
        loadcells = []
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
                    loadcells.append(BlueprintCell(self.celldict[cls], (None, (x, y))))
                curse += 1
        return loadcells


    def insert(self, cell, x, y):
        pass

    def get(self, tlx, tly, w, h):
        pass

    def delete(self, cell, x, y):
        pass

    def get_batches(self, tlx, tly, w, h):
        return []

    def unseeded(self, x, y):
        return False

    def _alias(self, x, y):
        pass

    def seed(self, x, y, cells):
        pass

    def set_map(self, map_token):
        self.active_map = self.maps[map_token]

