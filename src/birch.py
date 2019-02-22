import sys, pygame, json
from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE, QUIT, VIDEORESIZE, \
    KEYUP, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_q
from time import sleep
import math

from texture_store import TextureStore
from cells.cell import Cell
from cells.uranium import Uranium
from engine import Engine
from random import randint

textures = TextureStore('../assets/');
cells = []
for y in range(25):
    cells.append([])
    for x in range(25):
        if randint(0,100) < 3:
            cells[y].append(Uranium(textures, (x, y)))
        else:
            cells[y].append(Cell("dirt", textures, (x, y)))

engine = Engine({
    "cells": cells,
    "money": 10000,
    "population": 0,
    "speed": 1,
    })

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
    message = "Cursor: %d, %d   Ticks: %d" % (pos[0], pos[1], engine.ticks)
    text = font.render(message, 1, BLACK)
    screen.blit(text, (5, 5))
    text = font.render(message, 1, RED)
    screen.blit(text, (4, 4))

pygame.mouse.set_visible(False)

while 1:
    engine.tick()
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
    for row in engine.state['cells']:
        for cell in row:
            cell.draw(camera, screen)
    screen.blit(textures["cursor"], real_cursor)
    drawPos(cursor_game_position)
    pygame.display.flip()
    sleep(sleeptime)
