from cells.cell import Cell
from random import randint

class Uranium(Cell):

    def __init__(self, textures, position):
        super().__init__("uranium", textures, position)
        self.decay_left = randint(200, 300)
        self.ticks = 0

    def tick(self, ticks, engine):
        damage = False
        if self.decay_left > 0:
            self.decay_left -= ticks - self.ticks
        if self.decay_left <= 0:
            engine.set_cell(self.position[0], self.position[1], Cell(
                "dirt", self.textures, self.position))
            print("decay", self.position)
            damage = True
        self.ticks = ticks
        return damage
