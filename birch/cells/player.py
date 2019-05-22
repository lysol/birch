from birch.cells.cell import Cell

class Player(Cell):

    def __init__(self, name, textures, position, texture_prefix, batch=None,
            size=None):
        self.texture_prefix = texture_prefix
        self.direction = '_d'
        self.texture_name = texture_prefix + self.direction
        super().__init__(name, textures, position, self.texture_name, batch=batch,
            size=size)
        self.speed = 2
        self.velocity = (0, 0)

    def go_up(self):
        self.velocity = (self.velocity[0], self.speed)
        self.direction = '_u'
        self.set_image()

    def go_down(self):
        self.velocity = (self.velocity[0], -self.speed)
        self.direction = '_d'
        self.set_image()

    def go_left(self):
        self.velocity = (-self.speed, self.velocity[1])
        self.direction = '_l'
        self.set_image()

    def go_right(self):
        self.velocity = (self.speed, self.velocity[1])
        self.direction = '_r'
        self.set_image()

    def apply_movement(self):
        self.position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1]
            )
        self.velocity = (0, 0)

    def set_image(self):
        self.texture_name = self.texture_prefix + self.direction
        self.image = self.textures[self.texture_name]

