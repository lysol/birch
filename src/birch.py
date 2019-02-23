import sys, pygame, json
from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE, QUIT, VIDEORESIZE, \
    KEYUP, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_q, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from time import sleep
import math

from texture_store import TextureStore
from toolbox import Toolbox
from cells.cell import Cell
from cells.uranium import Uranium
from engine import Engine
from random import randint

dimensions = 100, 100

textures = TextureStore('../assets/');
cells = []
for y in range(dimensions[1]):
    cells.append([])
    for x in range(dimensions[0]):
        if randint(0,100) < 3:
            cells[y].append(Uranium(textures, (x, y)))
        else:
            cells[y].append(Cell("dirt", textures, (x, y)))

engine = Engine({
    "cells": cells,
    "money": 10000,
    "population": 0,
    "speed": 1,
    }, textures)

keys = [];
mouse_down = [False, False]
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

fps = 60
sleeptime = 1 / fps

font = pygame.font.Font(None, 24)
damage = True

toolbox = Toolbox([
    "bulldoze", "r", "c", "i"
    ], textures)

def drawPos(pos):
    message = "Cursor: %d, %d   Ticks: %d" % (pos[0], pos[1], engine.ticks)
    text = font.render(message, 1, BLACK)
    screen.blit(text, (5, 5))
    text = font.render(message, 1, RED)
    screen.blit(text, (4, 4))


while 1:
    changed_cells = engine.tick()
    for event in pygame.event.get():
        if event.type == QUIT: sys.exit()
        if event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
            size = event.dict['size']
        if event.type == KEYDOWN and event.key not in keys:
            keys.append(event.key)
        if event.type == KEYUP and event.key in keys:
            keys.remove(event.key)
        if event.type == MOUSEBUTTONDOWN and not mouse_down[0]:
            damage = True
            mouse_down[0] = True
        if event.type == MOUSEBUTTONUP and mouse_down[0]:
            damage = True
            mouse_down[0] = False

    for key in keys:
        if key == K_q:
            sys.exit()
        elif key == K_DOWN:
            camera[1] -= camera_speed
            damage = True
        elif key == K_UP:
            camera[1] += camera_speed
            damage = True
        elif key == K_RIGHT:
            camera[0] -= camera_speed
            damage = True
        elif key == K_LEFT:
            camera[0] += camera_speed
            damage = True
    pos = pygame.mouse.get_pos()
    rel = pygame.mouse.get_rel()
    print(rel)
    if rel[0] != 0 or rel[1] != 0:
        damage = True
    real_cursor = [
        math.floor(pos[0] / 32) * 32 + camera[0] % 32,
        math.floor(pos[1] / 32) * 32 + camera[1] % 32
    ]
    cursor = list(pos)
    cursor_game_position = [
        math.floor(math.floor(cursor[0] / 32)) - math.floor(camera[0] / 32),
        math.floor(math.floor(cursor[1] / 32)) - math.floor(camera[1] / 32)
    ];

    size = screen.get_size()
    cellw = math.ceil(size[0] / 32.0)
    cellh = math.ceil(size[1] / 32.0)
    min_x = max(math.floor(-camera[0] / 32.0 - 1), 0)
    min_y = max(math.floor(-camera[1] / 32.0 - 1), 0)
    max_x = min_x + cellw + 2
    max_y = min_y + cellh + 2
    for c in changed_cells:
        if c.position[0] >= min_x and c.position[0] <= max_x and \
            c.position[1] >= min_y and c.position[1] <= max_y:
            damage = True
            break
    if toolbox.in_bounds(pos):
        pygame.mouse.set_visible(True)
        if mouse_down[0]:
            toolbox.selected = toolbox.hover_icon(pos)
    else:
        pygame.mouse.set_visible(False)
        if mouse_down[0]:
            engine.use_tool(toolbox.tools[toolbox.selected],
                cursor_game_position)
            damage = True
    if damage:
        print("B A T T L E   D A M A G E")
        toolbox.cache_draw()
        screen.fill(BLACK)
        for row in engine.state['cells'][min_y:max_y]:
            for cell in row[min_x:max_x]:
                cell.draw(camera, screen)
        screen.blit(textures["cursor"], real_cursor)
        toolbox.draw(screen)
        drawPos(cursor_game_position)
        pygame.display.flip()
    damage = False
    sleep(sleeptime)
