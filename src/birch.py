import sys, pygame, math, json
from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE, QUIT, VIDEORESIZE, \
    KEYUP, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_q, MOUSEBUTTONDOWN, MOUSEBUTTONUP, \
    Rect, K_d, K_LSHIFT, K_RSHIFT
from time import sleep
from random import randint

from texture_store import TextureStore
from toolbox import Toolbox
from statusbox import Statusbox
from rcibox import RCIbox
from cells.cell import Cell
from cells.uranium import Uranium
from cells.tree import PineTree, BirchTree
from engine import Engine
import cursor


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        else:
            return repr(o)

jsonenc = ObjectEncoder()

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
        elif randint(0, 100) < 5:
            cells[y].append(BirchTree(textures, (x, y)))
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
pygame.display.set_caption('birch')

size = 800, 600
speed = [2, 2]
BLACK = 0, 0, 0
RED = 255, 0, 0
WHITE = 255, 255, 255
camera = [0, 0]
camera_speed = 8
cursor_speed = 8
screen = pygame.display.set_mode(size, HWSURFACE | DOUBLEBUF | RESIZABLE)

fps = 60
sleeptime = 1 / fps
time_spent = 0
kf_interval = 0.5
next_kf = 0.5
rci_refresh = 0
last_speed_change = 0
speed_delay = 0.1

edge_delay = 0.5
font = pygame.font.Font(None, 24)
damage = True
edged = -1
toolbox = Toolbox([
    "bulldoze", "r_0_0", "c_0_0", "i_0_0"
    ], textures)
rcibox = RCIbox()
statusbox = Statusbox(textures, engine)

def drawPos(pos):
    message = "Cursor: %d, %d   Ticks: %d" % (pos[0], pos[1], engine.ticks)
    text = font.render(message, 1, BLACK)
    screen.blit(text, (5, 5))
    text = font.render(message, 1, RED)
    screen.blit(text, (4, 4))

def pos_to_cell(pos, camera):
    return [
        math.floor(math.floor(pos[0] / 32)) - math.floor(camera[0] / 32),
        math.floor(math.floor(pos[1] / 32)) - math.floor(camera[1] / 32)
    ];

pygame.mixer.quit()
last_cursor = (None, None)
cursor_damage = False

scrolling = False
scroll_pos = 0, 0
cursor_changed = False

while 1:
    size = screen.get_size()
    pos = pygame.mouse.get_pos()
    rel = pygame.mouse.get_rel()
    update_rects = []
    changed_cells = engine.tick()
    pygame.mouse.set_visible(False)
    if next_kf <= time_spent:
        next_kf = time_spent + kf_interval
        damage = True
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
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
        if event.type == KEYDOWN and event.key == K_d:
            for row in engine.state["cells"]:
                for cell in row:
                    if hasattr(cell, 'population'):
                        print("cell", cell.position, cell.name, cell.population, cell.level)

    for key in keys:
        if key in (K_DOWN, K_UP, K_RIGHT, K_LEFT):
            damage = True
        if key in (K_LSHIFT, K_RSHIFT):
            if not scrolling:
                scroll_pos = pos
                cursor.set_cursor("scroll")
            scrolling = True
            cursor_changed = True
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

    if scrolling:
        if K_LSHIFT not in keys and K_RSHIFT not in keys:
            scrolling = False
            scroll_pos = (0, 0)
            cursor_changed = False
            cursor.set_cursor("arrow")
        else:
            pygame.mouse.set_visible(True)

    if pygame.mouse.get_focused() and not scrolling:
        if pos[0] <= 16:
            if edged == -1:
                edged = time_spent
            if time_spent - edged > edge_delay:
                camera[0] += camera_speed
                damage = True
        elif pos[0] >= size[0] - 16:
            if edged == -1:
                edged = time_spent
            if time_spent - edged > edge_delay:
                camera[0] -= camera_speed
                damage = True
        elif pos[1] <= 16:
            if edged == -1:
                edged = time_spent
            if time_spent - edged > edge_delay:
                camera[1] += camera_speed
                damage = True
        elif pos[1] >= size[1] - 16:
            if edged == -1:
                edged = time_spent
            if time_spent - edged > edge_delay:
                camera[1] -= camera_speed
                damage = True
        else:
            edged = -1
    if pygame.mouse.get_focused() and scrolling:
        camera[0] += rel[0]
        camera[1] += rel[1]
        damage = True
    else:
        edged = -1

    real_cursor = [
        math.floor(pos[0] / 32) * 32 + camera[0] % 32,
        math.floor(pos[1] / 32) * 32 + camera[1] % 32
    ]
    cursor_game_position = pos_to_cell(pos, camera)
    last_game_position = pos_to_cell((pos[0] + rel[0], pos[1] + rel[1]), camera)

    cellw = math.ceil(size[0] / 32.0)
    cellh = math.ceil(size[1] / 32.0)
    min_x = max(math.floor(-camera[0] / 32.0 - 1), 0)
    min_y = max(math.floor(-camera[1] / 32.0 - 1), 0)
    max_x = min_x + cellw + 2
    max_y = min_y + cellh + 2
    rcivals = list(map(lambda k: engine.state["demand"][k],
        ['r', 'c', 'i']))
    if time_spent >= rci_refresh:
        rcibox.cache_draw(*rcivals)
        update_rects.append(rcibox.draw(screen))
        rci_refresh = time_spent + kf_interval
    if damage:
        screen.fill(BLACK)
        changed_cells = []
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                changed_cells.append((x, y))
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
        draw_cursor = False
    elif statusbox.in_bounds(pos):
        pygame.mouse.set_visible(True)
        if statusbox.speed_icon_hover(pos):
            if not cursor_changed:
                cursor.set_cursor("pointer")
                cursor_changed = True
            if mouse_down[0] and time_spent >= last_speed_change + speed_delay:
                engine.state["speed"] = (engine.state["speed"] + 1) % len(statusbox.speeds)
                last_speed_change = time_spent
                next_kf = time_spent
        elif cursor_changed and not scrolling:
            cursor.set_cursor("arrow")
            cursor_changed = False
        draw_cursor = False
    else:
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
        cell = engine.get_cell(*c)
        if cell is not None:
            update_rects.append(cell.draw(camera, screen))
    if draw_cursor and not scrolling:
        update_rects.append(screen.blit(textures["cursor"], real_cursor))
    update_rects.append(toolbox.draw(screen))
    update_rects.append(statusbox.draw(screen, engine.state["speed"]))
    update_rects.append(rcibox.draw(screen))
    if damage:
        pygame.display.flip()
    else:
        pygame.display.update(update_rects)
    damage = False
    draw_cursor = False
    last_cursor = cursor_game_position
    sleep(sleeptime)
    time_spent += sleeptime
