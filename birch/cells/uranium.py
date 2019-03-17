from random import randint
from birch.cells.cell import Cell

class Uranium(Cell):

    def __init__(self, textures, position):
        super().__init__("uranium", textures, position, "uranium")
        self.next_tick = randint(200, 300)

    def tick(self, ticks, engine):
        engine.del_cell(self)
        damage = True
        self.ticks = ticks
        return damage
