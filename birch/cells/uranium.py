from random import randint
from birch.cells.cell import Cell

class Uranium(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("uranium", textures, position, "uranium", batch=batch)
        self.next_tick = randint(200, 300)

    def update(self, dt):
        #engine.del_cell(self)
        damage = True
        self.ticks = ticks
        return damage
