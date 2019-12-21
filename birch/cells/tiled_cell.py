from birch.cells.cell import Cell

class TiledCell(Cell):

    def __init__(self, properties, textures, position, size=[16, 16]):
        super().__init__(properties['name'], textures, position, properties['name'], size=size)
        otherprops = dict(properties)
        del(otherprops['name'])
        for k, v in otherprops.items():
            setattr(self, k, v)

