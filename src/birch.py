import sys, pygame, json
from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE, QUIT, VIDEORESIZE, \
    KEYUP, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_q
from time import sleep

names = json.load(open('../assets/names.json'))
textures = {}
for name in names.values():
    textures[name] = pygame.transform.scale2x(pygame.image.load("../assets/%s.png" % name))

cells = [["dirt"] * 25] * 25
keys = [];
pygame.init()

size = 800, 600
speed = [2, 2]
black = 0, 0, 0
camera = [0, 0]
cursor = [0, 0]
cursor_speed = 2
screen = pygame.display.set_mode(size, HWSURFACE | DOUBLEBUF | RESIZABLE)
ballrect = textures["r"].get_rect()

fps = 30
sleeptime = 1 / fps

while 1:
    for event in pygame.event.get():
        if event.type == QUIT: sys.exit()
        if event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
            size = event.dict['size']
        if event.type == KEYDOWN and event.key not in keys:
            keys.append(event.key)
        if event.type == KEYUP and event.key in keys:
            keys.remove(event.key)
    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > size[0]:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > size[1]:
        speed[1] = -speed[1]

    for key in keys:
        if key == K_q:
            sys.exit()
        elif key == K_UP and cursor[1] > 0:
            cursor[1] -= cursor_speed
        elif key == K_DOWN and cursor[1] < len(cells) * 32:
            cursor[1] += cursor_speed
        elif key == K_LEFT and cursor[0] > 0:
            cursor[0] -= cursor_speed
        elif key == K_RIGHT and cursor[0] < len(cells[0]) * 32:
            cursor[0] += cursor_speed


    screen.fill(black)
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            coords = (x * 32, y * 32)
            screen.blit(textures[cells[y][x]], coords)
    screen.blit(textures["cursor"], cursor)
    pygame.display.flip()
    sleep(sleeptime)
