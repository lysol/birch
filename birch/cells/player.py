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

    def stop_moving(self):
        self.velocity = (0, 0)

    def go_up(self):
        self.velocity = (self.velocity[0], self.speed)
        if self.direction != '_u_walk':
            self.direction = '_u_walk'
            self.set_image()

    def go_down(self):
        self.velocity = (self.velocity[0], -self.speed)
        if self.direction != '_d_walk':
            self.direction = '_d_walk'
            self.set_image()

    def go_left(self):
        self.velocity = (-self.speed, self.velocity[1])
        if self.direction != '_l_walk':
            self.direction = '_l_walk'
            self.set_image()

    def go_right(self):
        self.velocity = (self.speed, self.velocity[1])
        if self.direction != '_r_walk':
            self.direction = '_r_walk'
            self.set_image()

    @property
    def next_movement(self):
        return (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1]
            )

    def apply_movement(self):
        if self.velocity == (0, 0) and self.direction.endswith('_walk'):
            self.direction = self.direction[:-5]
            self.set_image()
            return
        self.position = self.next_movement
        self.velocity = (0, 0)

    def set_image(self):
        self.texture_name = self.texture_prefix + self.direction
        self.image = self.textures[self.texture_name]

