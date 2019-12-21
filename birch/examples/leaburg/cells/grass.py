from birch.cells.cell import Cell

class Grass(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("grass", textures, position, "grass", batch=batch)

class Grass2(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("grass_light", textures, position, "grass_light", batch=batch)

class Grass3(Cell):

    def __init__(self, textures, position, batch=None):
        super().__init__("grass_light2", textures, position, "grass_light2", batch=batch)

