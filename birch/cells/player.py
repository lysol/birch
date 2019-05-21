from birch.cells.cell import Cell

class Player(Cell):

    def __init__(self, name, textures, position, texture_prefix, batch=None,
            size=None):
        self.texture_prefix = texture_prefix
        self.direction = '_d'
        super().__init__(name, textures, position, self.texture_name, batch=batch,
            size=size)
        self.speed = 2
        self.velocity = (0, 0)

    def go_up(self):
        self.velocity = (self.velocity[0], self.speed)
        self.direction = '_u'

    def go_down(self):
        self.velocity = (self.velocity[0], -self.speed)
        self.direction = '_d'

    def go_left(self):
        self.velocity = (-self.speed, self.velocity[1])
        self.direction = '_l'

    def go_right(self):
        self.velocity = (self.speed, self.velocity[1])
        self.direction = '_r'

    def apply_movement(self):
        self.position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1]
            )
        self.velocity = (0, 0)

    @property
    def texture_name(self):
        return '%s%s' % (self.texture_prefix, self.direction)

    @texture_name.setter
    def texture_name(self, name):
        self.texture_prefix = name

