from random import randint
from birch.util import clamp
from birch.cells.cell import Cell

def psum(n):
    return sum(map(lambda x: x + 1, range(n)))

level_thresholds = list(map(lambda l: psum(l + 1), range(10)))

class PopCell(Cell):

    level_threshold = 20
    max_level = 2

    def __init__(self, base_texture_name, textures, position, size=None):
        self.level = 0
        self.variety = randint(0,1)
        self.base_texture_name = base_texture_name
        super().__init__(base_texture_name,
            textures, position, self.texture_name, size=size)
        self.texture_name = base_texture_name
        self.population = 0
        self.demand = 0
        self.last_rci = 0

    def impassible(self, cell):
        return True

    def populate(self):
        if randint(0, 1000) < 2:
            self.population += randint(-1, 1)
        if self.demand > 0:
            self.population += 1
        elif self.demand < 0:
            self.population -= 1
        if self.population < 0:
            self.population = 0

    def _levelclamp(self, l):
        return clamp(l, 0, self.max_level)

    def level_check(self):
        if self.level != self.max_level:
            next_level = level_thresholds[self.level + 1]
            if self.population > next_level and randint(0, 100) < 25:
                self.level += 1
                self.image = self.textures[self.texture_name]

    @property
    def texture_name(self):
        return "%s_%d_%d" % (
            self.base_texture_name,
            self.variety,
            self._levelclamp(self.level)
        )

    @texture_name.setter
    def texture_name(self, value):
        self.base_texture_name = value


class RCell(PopCell):

    def __init__(self, textures, position):
        super().__init__("r", textures, position)


class CCell(PopCell):

    def __init__(self, textures, position):
        super().__init__("c", textures, position)


class ICell(PopCell):

    def __init__(self, textures, position):
        super().__init__("i", textures, position)

