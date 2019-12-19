"""
implements a world class that can
* select different scenes/maps
* use data from the Tiled map editor
"""
class TiledWorld:
    def __init__(self):
        pass

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
