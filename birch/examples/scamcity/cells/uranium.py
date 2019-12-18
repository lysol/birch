from random import randint
from birch.cells.cell import Cell

class Uranium(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("uranium", textures, position, "uranium", batch=batch)
        self.next_update = randint(50, 400)

    def update(self, ticks, engine):
        engine.del_cell(self)
        damage = True
        return damage
