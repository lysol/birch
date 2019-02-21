import sys, pygame, json

names = json.load(open('../assets/names.json'))
textures = {}
for name in names.values():
    textures[name] = pygame.transform.scale2x(pygame.image.load("../assets/%s.png" % name))

cells = [["dirt"] * 25] * 25
print(cells)
pygame.init()

size = 800, 600
speed = [2, 2]
black = 0, 0, 0
camera = 0, 0
cursor = 0, 0
screen = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
ballrect = textures["r"].get_rect()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict['size'], pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            size = event.dict['size']
    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > size[0]:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > size[1]:
        speed[1] = -speed[1]

    screen.fill(black)
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            coords = (x * 32, y * 32)
            screen.blit(textures[cells[y][x]], coords)
    screen.blit(textures["cursor"], cursor)
    pygame.display.flip()
