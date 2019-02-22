import sys, pygame, json
from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE, QUIT, VIDEORESIZE, \
    KEYUP, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_q, MOUSEBUTTONDOWN, MOUSEBUTTONUP, \
    Rect
from time import sleep
import math

from texture_store import TextureStore
from toolbox import Toolbox
from cells.cell import Cell
from cells.uranium import Uranium
from cells.tree import PineTree
from engine import Engine
from random import randint
dimensions = 100, 100

textures = TextureStore('../assets/');
cells = []
for y in range(dimensions[1]):
    cells.append([])
    for x in range(dimensions[0]):
        if randint(0, 100) < 3:
            cells[y].append(Uranium(textures, (x, y)))
        elif randint(0, 100) < 5:
            cells[y].append(PineTree(textures, (x, y)))
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
kf_interval = 200
next_kf = 200

edge_delay = 20
font = pygame.font.Font(None, 24)
damage = True
edged = -1
toolbox = Toolbox([
    "bulldoze", "r", "c", "i"
    ], textures)

def drawPos(pos):
    message = "Cursor: %d, %d   Ticks: %d" % (pos[0], pos[1], engine.ticks)
    text = font.render(message, 1, BLACK)
    screen.blit(text, (5, 5))
    text = font.render(message, 1, RED)
    screen.blit(text, (4, 4))

def cursor_to_cell(cursor, camera):
    return [
        math.floor(math.floor(cursor[0] / 32)) - math.floor(camera[0] / 32),
        math.floor(math.floor(cursor[1] / 32)) - math.floor(camera[1] / 32)
    ];

pygame.mixer.quit()
last_cursor = (None, None)
cursor_damage = False

while 1:
    update_rects = []
    changed_cells = engine.tick()
    if next_kf <= engine.ticks:
        next_kf = engine.ticks + kf_interval
        damage = True
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
            mouse_down[0] = True
        if event.type == MOUSEBUTTONUP and mouse_down[0]:
            mouse_down[0] = False

    for key in keys:
        if key in (K_DOWN, K_UP, K_RIGHT, K_LEFT):
            damage = True
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
    size = screen.get_size()
    pos = pygame.mouse.get_pos()
    rel = pygame.mouse.get_rel()

    if pos[0] <= 16:
        if edged == -1:
            edged = engine.ticks
        if engine.ticks - edged > edge_delay:
            camera[0] += camera_speed
            damage = True
    elif pos[0] >= size[0] - 16:
        if edged == -1:
            edged = engine.ticks
        if engine.ticks - edged > edge_delay:
            camera[0] -= camera_speed
            damage = True
    elif pos[1] <= 16:
        if edged == -1:
            edged = engine.ticks
        if engine.ticks - edged > edge_delay:
            camera[1] += camera_speed
            damage = True
    elif pos[1] >= size[1] - 16:
        if edged == -1:
            edged = engine.ticks
        if engine.ticks - edged > edge_delay:
            camera[1] -= camera_speed
            damage = True
    else:
        edged = -1

    real_cursor = [
        math.floor(pos[0] / 32) * 32 + camera[0] % 32,
        math.floor(pos[1] / 32) * 32 + camera[1] % 32
    ]
    cursor = list(pos)
    cursor_game_position = cursor_to_cell(cursor, camera)
    last_game_position = cursor_to_cell((cursor[0] + rel[0], cursor[1] + rel[1]), camera)

    cellw = math.ceil(size[0] / 32.0)
    cellh = math.ceil(size[1] / 32.0)
    min_x = max(math.floor(-camera[0] / 32.0 - 1), 0)
    min_y = max(math.floor(-camera[1] / 32.0 - 1), 0)
    max_x = min_x + cellw + 2
    max_y = min_y + cellh + 2
    if damage:
        screen.fill(BLACK)
        changed_cells = []
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                changed_cells.append((x, y))
        update_rects.append(toolbox.draw(screen))
        draw_cursor = True
    if cursor_damage and (cursor_game_position[0] != last_cursor[0] or cursor_game_position[1] != last_cursor[1]):
        changed_cells.append(last_cursor)
        cursor_damage = False
    if rel[0] != 0 or rel[1] != 0:
        cursor_damage = True
        draw_cursor = True
    if toolbox.in_bounds(pos):
        pygame.mouse.set_visible(True)
        if mouse_down[0]:
            toolbox.selected = toolbox.hover_icon(pos)
    else:
        pygame.mouse.set_visible(False)
        if mouse_down[0]:
            engine.use_tool(toolbox.tools[toolbox.selected],
                cursor_game_position)
            changed_cells.append(cursor_game_position)
            update_rects.append(Rect((
                pos[0] - 32,
                pos[1] - 32,
                64, 64)))
            draw_cursor = True

    # draw map first
    for c in changed_cells:
        update_rects.append(engine.get_cell(*c).draw(camera, screen))
    if draw_cursor:
        update_rects.append(screen.blit(textures["cursor"], real_cursor))
    update_rects.append(toolbox.draw(screen))
    if damage:
        pygame.display.flip()
    else:
        pygame.display.update(update_rects)
    damage = False
    draw_cursor = False
    last_cursor = cursor_game_position
    sleep(sleeptime)
