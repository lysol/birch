class Cell:

    def __init__(self, texture_name, textures, position):
        self.texture_name = texture_name
        self.textures = textures
        self.position = position

    def draw(self, camera, screen):
        coords = (
            self.position[0] * 32 + camera[0],
            self.position[1] * 32 + camera[1]
        )
        screen.blit(self.textures[self.texture_name], coords)
