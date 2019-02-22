from cells.cell import Cell
from random import randint

class Uranium(Cell):

    def __init__(self, textures, position):
        super().__init__("uranium", textures, position)
        self.next_tick = randint(200, 300)

    def tick(self, ticks, engine):
        engine.set_cell(self.position[0], self.position[1], Cell(
            "dirt", self.textures, self.position))
        damage = True
        self.ticks = ticks
        return damage
