from random import randint
from birch.cells.cell import Cell

class Tree(Cell):

    def __init__(self, texture_name, textures, position, age=None, batch=None):
        super().__init__(texture_name, textures, position, texture_name, batch=batch)
        self.age = age if age is not None else randint(0, 100)
        self.base_texture_name = texture_name
        self.next_update = randint(25, 50)

    def impassible(self, cell):
        return True

    @property
    def texture_name(self):
        return self.base_texture_name if hasattr(self, 'age') and self.age > 50 else '%s_sapling' % self.base_texture_name

    @texture_name.setter
    def texture_name(self, value):
        self.base_texture_name = value

    def update(self, ticks, engine):
        self.age += 1
        self.next_update = ticks + randint(25, 50)


class PineTree(Tree):

    def __init__(self, textures, position, batch=None):
        super().__init__("pine_tree", textures, position, batch=batch)

class BirchTree(Tree):

    def __init__(self, textures, position, batch=None):
        super().__init__("birch_tree", textures, position, batch=batch)
