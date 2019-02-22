import sys, pygame, json
from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE, QUIT, VIDEORESIZE, \
    KEYUP, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_q
from time import sleep
import math

names = json.load(open('../assets/names.json'))
textures = {}
for name in names.values():
    textures[name] = pygame.transform.scale2x(pygame.image.load("../assets/%s.png" % name))

cells = [["dirt"] * 25] * 25
keys = [];
pygame.init()

size = 800, 600
speed = [2, 2]
BLACK = 0, 0, 0
RED = 255, 0, 0
WHITE = 255, 255, 255
camera = [0, 0]
cursor = [0, 0]
camera_speed = 8
cursor_speed = 8
screen = pygame.display.set_mode(size, HWSURFACE | DOUBLEBUF | RESIZABLE)
ballrect = textures["r"].get_rect()

fps = 30
sleeptime = 1 / fps

font = pygame.font.Font(None, 24)

def drawPos(pos):
    text = font.render("%d, %d" % (pos[0], pos[1]), 1, BLACK)
    screen.blit(text, (5, 5))
    text = font.render("%d, %d" % (pos[0], pos[1]), 1, RED)
    screen.blit(text, (4, 4))

pygame.mouse.set_visible(False)

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
        elif key == K_DOWN:
            camera[1] -= camera_speed
        elif key == K_UP:
            camera[1] += camera_speed
        elif key == K_RIGHT:
            camera[0] -= camera_speed
        elif key == K_LEFT:
            camera[0] += camera_speed
    pos = pygame.mouse.get_pos()
    real_cursor = [
        math.floor(pos[0] / 32) * 32 + camera[0] % 32,
        math.floor(pos[1] / 32) * 32 + camera[1] % 32
    ]
    cursor = list(pos)
    cursor_game_position = [
        math.floor(math.floor(cursor[0] / 32)) - math.floor(camera[0] / 32),
        math.floor(math.floor(cursor[1] / 32)) - math.floor(camera[1] / 32)
    ];

    screen.fill(BLACK)
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            coords = (x * 32 + camera[0], y * 32 + camera[1])
            screen.blit(textures[cells[y][x]], coords)
    screen.blit(textures["cursor"], real_cursor)
    drawPos(cursor_game_position)
    pygame.display.flip()
    sleep(sleeptime)
