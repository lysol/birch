from random import randint
from datetime import timedelta, datetime
from birch.cells.cell import Cell

class Uranium(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("uranium", textures, position, "uranium", batch=batch)
        self.next_update = datetime.now() + timedelta(0, randint(5, 30))

    def update(self, dt, engine):
        engine.del_cell(self)
        damage = True
        return damage
