import sys, pygame, math, json
from time import sleep
from random import randint

from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE, QUIT, VIDEORESIZE, \
    KEYUP, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_q, MOUSEBUTTONDOWN, MOUSEBUTTONUP, \
    Rect, K_d, K_LSHIFT, K_RSHIFT

from texture_store import TextureStore
from toolbox import Toolbox
from statusbox import Statusbox
from rcibox import RCIbox
from engine import Engine
from cells.cell import Cell
from cells.uranium import Uranium
from cells.tree import PineTree, BirchTree
from util import RED, BLUE, FG_COLOR, BG_COLOR
import cursor


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        else:
            return repr(o)


class Game:

    tools = (
        "bulldoze",
        "r_0_0",
        "c_0_0",
        "i_0_0",
        "road_h"
        )

    damage_keys = K_DOWN, K_UP, K_RIGHT, K_LEFT
    screen_flags = (HWSURFACE | DOUBLEBUF | RESIZABLE)
    edge_scroll_width = 16

    def __init__(self, initial_dims):
        self.textures = TextureStore('../assets/')
        self.initial_dims = initial_dims
        self.engine = Engine({
            "cells": [],
            "money": 10000,
            "population": 0,
            "speed": 1
            }, self.textures, dimensions=initial_dims)
        self.mouse_down = [False, False]
        self.size = 800, 600
        self.scroll_speed = [2, 2]
        self.camera = [0, 0]
        self.camera_speed = 8
        self.cursor_speed = 8
        self.screen = None
        self.fps = 60
        self.sleeptime = 1 / self.fps
        self.time_spent = 0
        self.kf_interval = 0.5
        self.speed_delay = 0.1
        self.edge_delay = 0.5
        self.scroll_pos = 0, 0
        self.jsonenc = ObjectEncoder()

    def init_cells(self, dimensions):
        cells = []
        for y in range(0, dimensions[1], 32):
            for x in range(0, dimensions[0], 32):
                if randint(0, 100) < 3:
                    cells.append(Uranium(self.textures, (x, y)))
                elif randint(0, 100) < 5:
                    cells.append(PineTree(self.textures, (x, y)))
                elif randint(0, 100) < 5:
                    cells.append(BirchTree(self.textures, (x, y)))
                elif randint(0, 100) < 20:
                    cells.append(Cell('dirt', self.textures, (x, y)))
        for cell in cells:
            self.engine.set_cell(cell)

    def aliased_camera(self, cursor_size):
        return (
            self.camera[0] - self.camera[0] % cursor_size,
            self.camera[1] - self.camera[1] % cursor_size
            )

    def init(self):
        self.init_cells(self.initial_dims)
        pygame.init()
        pygame.display.set_caption('birch')
        self.screen = pygame.display.set_mode(self.size, self.screen_flags)
        # reduce cpu usage, what a shitty bug
        pygame.mixer.quit()
        self.font = pygame.font.Font(None, 24)
        self.init_panels()

    def init_panels(self):
        self.toolbox = Toolbox(self.tools, self.textures)
        self.rcibox = RCIbox()
        self.statusbox = Statusbox(self.textures, self.engine)

    def get_mouse_pressed(self):
        return pygame.mouse.get_pressed()

    def console_dump(self):
        for cell in self.engine.state['cells']:
            if hasattr(cell, 'population'):
                print('cell', cell.position, cell.name, cell.population, cell.level)

    def run(self):
        damage = True
        size = self.screen.get_size()
        keys = []
        mouse_down = self.get_mouse_pressed()
        scrolling = False
        edged = -1

        cursor_size = 32
        cursor_changed = False
        cursor_damage = False
        screen_cursor_rect = Rect(0, 0, 32, 32)
        game_cursor_rect = screen_cursor_rect.copy()
        last_screen_cursor_rect = screen_cursor_rect.copy()
        last_game_cursor_rect = screen_cursor_rect.copy()

        last_speed_change = 0
        last_kf = 0
        next_kf = 0
        last_tool_time = 0 # uuuaaauuggh
        last_rci_time = 0
        debug = False
        while True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_rel = pygame.mouse.get_rel()
            update_rects = []
            changed_cells = self.engine.tick()
            pygame.mouse.set_visible(False)
            draw_cursor = False
            if next_kf <= self.time_spent:
                next_kf = self.time_spent + self.kf_interval
                damage = True

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        event.dict['size'], self.screen_flags)
                    size = event.dict['size']
                if event.type == KEYUP and event.key in keys:
                    keys.remove(event.key)
                if event.type == KEYDOWN and event.key not in keys:
                    keys.append(event.key)
                if K_d in keys:
                    self.console_dump()
                    debug = not debug
                if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                    mouse_down = self.get_mouse_pressed()


            for key in keys:
                if key in (K_DOWN, K_UP, K_RIGHT, K_LEFT):
                    damage = True
                if key in (K_LSHIFT, K_RSHIFT):
                    if not scrolling:
                        scroll_pos = mouse_pos
                        cursor.set_cursor("scroll")
                    scrolling = True
                    cursor_changed = True
                if key == K_q:
                    sys.exit()
                elif key == K_DOWN:
                    self.camera[1] += self.camera_speed
                elif key == K_UP:
                    self.camera[1] -= self.camera_speed
                elif key == K_RIGHT:
                    self.camera[0] += self.camera_speed
                elif key == K_LEFT:
                    self.camera[0] -= self.camera_speed

            if scrolling:
                if K_LSHIFT not in keys and K_RSHIFT not in keys:
                    scrolling = False
                    scroll_pos = 0, 0
                    cursor_changed = False
                    cursor.set_cursor("arrow")
                else:
                    pygame.mouse.set_visible(True)

            if pygame.mouse.get_focused() and not scrolling:
                if mouse_pos[0] <= self.edge_scroll_width:
                    if edged == -1:
                        edged = self.time_spent
                    if self.time_spent - edged > self.edge_delay:
                        self.camera[0] -= self.camera_speed
                        damage = True
                elif mouse_pos[0] >= size[0] - self.edge_scroll_width:
                    if edged == -1:
                        edged = self.time_spent
                    if self.time_spent - edged > self.edge_delay:
                        self.camera[0] += self.camera_speed
                elif mouse_pos[1] <= self.edge_scroll_width:
                    if edged == -1:
                        edged = self.time_spent
                    if self.time_spent - edged > self.edge_delay:
                        self.camera[1] -= self.camera_speed
                        damage = True
                elif mouse_pos[1] >= size[1] - self.edge_scroll_width:
                    if edged == -1:
                        edged = self.time_spent
                    if self.time_spent - edged > self.edge_delay:
                        self.camera[1] += self.camera_speed
                else:
                    edged = -1

            if pygame.mouse.get_focused() and scrolling:
                self.camera[0] += mouse_rel[0]
                self.camera[1] += mouse_rel[1]
                damage = True
            else:
                edged = -1

            aliased_mouse_pos = (
                mouse_pos[0] - mouse_pos[0] % cursor_size,
                mouse_pos[1] - mouse_pos[1] % cursor_size
                )

            aliased_camera_pos = self.aliased_camera(cursor_size)
            game_cursor_rect = Rect(
                aliased_mouse_pos[0] + aliased_camera_pos[0],
                aliased_mouse_pos[1] + aliased_camera_pos[1],
                cursor_size,
                cursor_size
                )

            screen_cursor_rect = Rect(
                aliased_mouse_pos[0] + cursor_size - self.camera[0] % cursor_size,
                aliased_mouse_pos[1] + cursor_size - self.camera[1] % cursor_size,
                cursor_size,
                cursor_size
                )

            game_cursor_rect = screen_cursor_rect.move(*self.camera)

            rcivals = list(map(lambda k: self.engine.state["demand"][k],
                ('r', 'c', 'i')))

            if self.time_spent >= last_rci_time:
                self.rcibox.cache_draw(*rcivals)
                rect = self.rcibox.draw(self.screen)
                update_rects.append(rect)
                last_rci_time = self.time_spent + self.kf_interval

            if damage:
                self.screen.fill(BG_COLOR)
                srect = self.screen.get_rect()
                nr = Rect(
                    srect.topleft[0] + self.camera[0],
                    srect.topleft[1] + self.camera[1],
                    srect.width,
                    srect.height)
                changed_cells.extend(self.engine.quad.get(nr))
                draw_cursor = True

            if cursor_damage and (
                screen_cursor_rect[0] != last_screen_cursor_rect.topleft[0] or \
                screen_cursor_rect[1] != last_screen_cursor_rect.topleft[1]):
                update_rects.append(screen_cursor_rect)
                update_rects.append(last_screen_cursor_rect)
                cell_damage = game_cursor_rect.copy()
                last_cell_damage = last_game_cursor_rect.copy()
                self.screen.fill(BG_COLOR, last_screen_cursor_rect)
                self.screen.fill(BG_COLOR, screen_cursor_rect)
                changed_cells.extend(self.engine.quad.get(cell_damage))
                changed_cells.extend(self.engine.quad.get(last_cell_damage))
                cursor_damage = False

            if mouse_rel[0] != 0 or mouse_rel[1] != 0:
                cursor_damage = True
                draw_cursor = True

            if self.toolbox.in_bounds(mouse_pos):
                pygame.mouse.set_visible(True)
                if mouse_down[0]:
                    hovered = self.toolbox.hover_icon(mouse_pos)
                    if hovered is not None:
                        self.toolbox.selected = hovered
                        cursor_size = self.toolbox.tool_size

                draw_cursor = False
            elif self.rcibox.in_bounds(mouse_pos):
                draw_cursor = False
                pass
            elif self.statusbox.in_bounds(mouse_pos):
                pygame.mouse.set_visible(True)
                if self.statusbox.speed_icon_hover(mouse_pos):
                    if not cursor_changed:
                        cursor.set_cursor("pointer")
                        cursor_changed = True
                    if mouse_down[0] and self.time_spent >= last_speed_change + self.speed_delay:
                        self.engine.state["speed"] = (
                            self.engine.state["speed"] + 1) % len(self.statusbox.speeds)
                        last_speed_change = self.time_spent
                        next_kf = self.time_spent
                    elif cursor_changed and not scrolling:
                        cursor.set_cursor("arrow")
                        cursor_changed = False
                    draw_cursor = False
            else:
                if mouse_down[0] and self.toolbox.selected is not None:
                    self.engine.use_tool(self.toolbox.tools[self.toolbox.selected], game_cursor_rect)
                    splash = game_cursor_rect.inflate([cursor_size * 2] * 2)
                    changed_cells.extend(self.engine.quad.get(splash))
                    update_rects.append(screen_cursor_rect)
                    draw_cursor = True

            # draw map first
            drawn = []
            for cell in filter(lambda c: self.screen.get_rect().colliderect(
                c.get_rect(self.camera)), changed_cells):
                if cell not in drawn:
                    if type(cell) == tuple:
                        print(cell)
                    update_rects.append(cell.draw(self.camera, self.screen))
                    if debug:
                        cell.draw_box(self.camera, self.screen, BLUE)
                    drawn.append(cell)

            if draw_cursor and not scrolling:
                update_rects.append(
                    self.screen.blit(self.textures["cursor_%d" % cursor_size], screen_cursor_rect))

            update_rects.append(self.statusbox.draw(self.screen, self.engine.state["speed"]))
            update_rects.append(self.toolbox.draw(self.screen))
            update_rects.append(self.rcibox.draw(self.screen))

            if debug:
                #for update_rect in update_rects:
                #    pygame.draw.rect(self.screen, RED, update_rect, 1)
                damage = True

            if damage:
                pygame.display.flip()
            else:
                pygame.display.update(update_rects)

            damage = False
            draw_cursor = False
            last_screen_cursor_rect = screen_cursor_rect
            last_game_cursor_rect = game_cursor_rect
            sleep(self.sleeptime)
            self.time_spent += self.sleeptime
