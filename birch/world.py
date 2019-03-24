import pyglet

class World:

    def __init__(self, chunk_size=1024):
        self.world = {}
        self.chunk_size = chunk_size
        self.seeded = {}
        self.batches = {}

    def _alias(self, x, y):
        return (
            int((x - x % self.chunk_size) / self.chunk_size),
            int((y - y % self.chunk_size) / self.chunk_size)
            )

    def unseeded(self, x, y):
        ox, oy = self._alias(x, y)
        return (ox, oy) not in self.seeded or not self.seeded[(ox, oy)]

    def _inflate(self, ix, iy, priority=10):
        changed = False
        priority = 10 if priority is None else priority
        if iy not in self.world:
            self.world[iy] = {}
            changed = True
        if ix not in self.world[iy]:
            self.world[iy][ix] = {}
            changed = True
        if changed:
            self.batches[(ix, iy)] = {}
            self.batches[(ix, iy)][priority] = pyglet.graphics.Batch()
            self.seeded[(ix, iy)] = False

    def insert(self, sprite, x, y):
        ox, oy = self._alias(x, y)
        priority = sprite.priority if hasattr(sprite, 'priority') else 10
        self._inflate(ox, oy, priority=priority)
        if priority not in self.batches[(ox, oy)]:
            self.batches[(ox, oy)][priority] = pyglet.graphics.Batch()
        sprite.batch = self.batches[(ox, oy)][priority]
        self.world[oy][ox][sprite.id] = sprite

    def delete(self, sprite, x, y):
        ox, oy = self._alias(x, y)
        self._inflate(ox, oy)
        sprite.batch = None
        del self.world[oy][ox][sprite.id]

    def get(self, x, y, w, h):
        chunks = self.get_chunks(x, y, w, h)
        out = []
        for chunk in chunks:
            for sprite_id in chunk:
                sprite = chunk[sprite_id]
                if sprite not in out and sprite.intersects(x, y, w, h):
                    out.append(sprite)
        return out

    def get_chunks(self, x, y, w = 1, h = 1):
        ox, oy = self._alias(x, y)
        px, py = self._alias(x + w, y + h)
        out = []
        for yes in list(range(oy, py + 1)):
            for xes in list(range(ox, px + 1)):
                self._inflate(xes, yes)
                out.append(self.world[yes][xes])
        return out

    def seed(self, ix, iy, sprites):
        if (ix, iy) in self.seeded and self.seeded[(ix, iy)]:
            return False
        for sprite in sprites:
            self.insert(sprite, *sprite.position)
        self.seeded[(ix, iy)] = True
        return True

    def get_batches(self, x, y, w, h):
        ox, oy = self._alias(x, y)
        px, py = self._alias(x + w, y + h)
        batch_draws = []
        #for cell in self.get(x, y, w, h):
        #    cell.set_pos((x, y))
        for yes in list(range(oy, py + 1)):
            for xes in list(range(ox, px + 1)):
                if (xes, yes) in self.batches:
                    bdict = self.batches[(xes, yes)]
                    pees = sorted(bdict.keys())
                    for p in pees:
                        batch_draws.append(bdict[p])
        return batch_draws

