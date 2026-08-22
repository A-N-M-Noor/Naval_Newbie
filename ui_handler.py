from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from naval_newbie import GameController

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math, random
import numpy as np

from utils import *
from inputs_handler import KeyboardInput, MouseInput
from camera_controller import CameraController
from entity_handler import Ship, Ships_Handler, SHIP_TYPE, Player, Bullet, Bullets_Handler, Island
from entity_handler import set_ships_handler, set_particles_manager, set_bullets_manager, set_islands
from particles import Particle, Particles



class UI:
    def __init__(self, game_controller: GameController):
        self.gc: GameController = game_controller

        self.current_menu = self.gc.game_state
        self.last_menu = self.gc.game_state

        self.btn_h = ButtonsHandler(self)

    def click(self, x, y):
        return self.btn_h.click(x, y)

    def draw_menu_hud(self):
        gc: GameController = self.gc
        btn_h: ButtonsHandler = self.btn_h

        btn_h.btn(Button(
            ID=0, 
            x=pN_Cx(0.5)-pN_Cy(0.1), y=pN_Cy(0.90), width=pN_Cy(0.2), height=pN_Cy(0.05), 
            text="Battle!", 
            button_type=ButtonType.DANGER, 
            callback=gc.switch_game_state, callback_args=(GameState.PLAYING,)
        ))

        btn_h.btn(Button(
            ID=1, 
            x=pN_Cx(0.95), y=pN_Cy(0.45), width=pN_Cy(0.05), height=pN_Cy(0.05), 
            text=">", 
            button_type=ButtonType.REGULAR, 
            callback=gc.switch_ship
        ))

        btn_h.btn(Button(
            ID=2, 
            x=pN_Cy(0.05), y=pN_Cy(0.05), width=pN_Cy(0.2), height=pN_Cy(0.05), 
            text="Quit", 
            button_type=ButtonType.REGULAR, 
            callback=quit_game
        ))

        btn_h.btn(Button(
            ID=3, 
            x=pN_Cy(0.30), y=pN_Cy(0.05), width=pN_Cy(0.2), height=pN_Cy(0.05), 
            text="Upgrade!", 
            button_type=ButtonType.WARNING, 
            callback=gc.switch_game_state, callback_args=(GameState.UPGRADES,)
        ))

        # btn_h.btn(Button(
        #     ID=3, 
        #     x=pN_Cy(0.25), y=pN_Cy(0.05), width=pN_Cy(0.2), height=pN_Cy(0.05), 
        #     text="Upgrade", 
        #     button_type=ButtonType.REGULAR, 
        #     callback=gc.switch_game_state, callback_args=(GameState.UPGRADE,)
        # ))

    def draw_ship_marker(self, ship: Ship):
        gc: GameController = self.gc

        marker_p = [ship.position[0], ship.position[1], ship.size[2] + 1.0]
        pos_x, pos_y, visible = conv_3d_2_2d(marker_p, gc.cam)

        if not visible:
            return
        
        if ship.hp == ship.max_hp:
            glColor3f(1.0, 0.0, 1.0)
            draw_line(pos_x-5, pos_y+5, pos_x, pos_y)
            draw_line(pos_x+5, pos_y+5, pos_x, pos_y)
            return

        if ship.alive:
            glColor3f(0.3, 0.3, 0.3)
            draw_rect(pos_x-pN_Cy(0.05), pos_y+pN_Cy(0.05), pN_Cy(0.1), pN_Cy(0.01))
            ht = ship.hp / ship.max_hp
            glColor3f(1.0, 0.0, 0.0)
            draw_rect(pos_x-pN_Cy(0.05), pos_y+pN_Cy(0.05), pN_Cy(0.1)*ht, pN_Cy(0.01))

    def mm_x(self, x):
        gc: GameController = self.gc

        ms = pN_Cy(0.3)
        map_size = 600

        return remap(x, -map_size, map_size, gc.WIDTH - ms, gc.WIDTH)

    def mm_y(self, y):
        ms = pN_Cy(0.3)
        map_size = 600

        return remap(y, -map_size, map_size, 0, ms)

    def draw_minimap(self):
        gc: GameController = self.gc

        ms = pN_Cy(0.3)
        map_size = 600
        
        glLineWidth(2.0)
        glColor3f(0.2, 0.9, 0.9)
        draw_rect(
            gc.WIDTH - ms, 0, ms, ms 
        )
        glColor3f(0.0, 0.0, 0.0)
        draw_rect_hollow(
            gc.WIDTH - ms, 0, ms, ms 
        )

        for island in gc.islands:
            for sub in island.sub_islands:
                x = self.mm_x(sub.position[0])
                y = self.mm_y(sub.position[1])
                glColor3f(sub.color[0], sub.color[1], sub.color[2])
                draw_filled_circle(x, y, remap(sub.size, 0, map_size*2, 0, ms/2), segments=10)

        for ship in gc.ships_handler.ships:
            x = self.mm_x(ship.position[0])
            y = self.mm_y(ship.position[1])
            if ship.ship_type == SHIP_TYPE.DESTROYER:
                glColor3f(1.0, 0.5, 0.0)
            else:
                glColor3f(1.0, 0.0, 0.5)
            if not ship.alive:
                glColor3f(0.2, 0.2, 0.2)
            draw_rect(x, y, pN_Cy(0.015), pN_Cy(0.0075), ship.heading)

        x = self.mm_x(gc.player.ship.position[0])
        y = self.mm_y(gc.player.ship.position[1])
        glColor3f(0.0, 0.0, 1.0)
        draw_rect(x, y, pN_Cy(0.015), pN_Cy(0.0075), gc.player.ship.heading)

        t_x = self.mm_x(gc.target_3D[0])
        t_y = self.mm_y(gc.target_3D[1])

        t_x = clamp(t_x, gc.WIDTH - ms, gc.WIDTH)
        t_y = clamp(t_y, 0, ms)

        glColor3f(1.0, 1.0, 0.0)
        draw_line(t_x, t_y+5, t_x, t_y-5)
        draw_line(t_x+5, t_y, t_x-5, t_y)

    def draw_ship_healtbar(self):
        gc: GameController = self.gc

        w = gc.WIDTH - pN_Cy(0.7)
        h = pN_Cy(0.06)
        x = gc.WIDTH/2 - w/2
        y = pN_Cy(0.05)

        glColor3f(0.2, 0.2, 0.2)
        draw_rect(x-2, y-2, w+4, h+4)
        glColor3f(0.15, 1.0, 0.25)
        ht = gc.player.ship.hp / gc.player.ship.max_hp
        if ht > 0.0:
            draw_rect(x, y, w * ht, h)

    def draw_playing_hud(self):
        gc: GameController = self.gc

        l = gc.player.ship.load_status * 90
        l_t = gc.player.ship.torpedo_load_status * 90
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(4.0)
        draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), 135, 225, segments=25)
        draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), -45, 45, segments=25)

        glLineWidth(2.0)
        glColor3f(0.0, 1.0, 0.0)
        draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), 225-l, 225, segments=25)
        draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), -45, -45+l_t, segments=25)

        glColor3f(0.2, 0.2, 0.2)
        draw_circle(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.01), segments=10)

        draw_line(pN_Cx(0.55), pN_Cy(0.5), pN_Cx(0.9), pN_Cy(0.5))
        draw_line(pN_Cx(0.45), pN_Cy(0.5), pN_Cx(0.1), pN_Cy(0.5))

        for i in range(10):
            x = 0.55 + i* ((0.9-0.55)/10)
            draw_line(pN_Cx(x), pN_Cy(0.495), pN_Cx(x), pN_Cy(0.505))

            x = 0.45 + i* ((0.1-0.45)/10)
            draw_line(pN_Cx(x), pN_Cy(0.495), pN_Cx(x), pN_Cy(0.505))

        for ship in gc.ships_handler.ships:
            self.draw_ship_marker(ship)

        self.draw_minimap()

        self.draw_ship_healtbar()

    def draw_paused_hud(self):
        gc: GameController = self.gc
        btn_h: ButtonsHandler = self.btn_h

        btn_h.btn(Button(
            ID=50, 
            x=pN_Cy(0.1), y=pN_Cy(0.5), width=pN_Cy(0.6), height=pN_Cy(0.05), 
            text="Resume", 
            button_type=ButtonType.SUCCESS, 
            callback=gc.switch_game_state, callback_args=(GameState.PLAYING,)
        ))

        btn_h.btn(Button(
            ID=51, 
            x=pN_Cy(0.1), y=pN_Cy(0.44), width=pN_Cy(0.6), height=pN_Cy(0.05), 
            text="Menu", 
            button_type=ButtonType.WARNING, 
            callback=gc.switch_game_state, callback_args=(GameState.MENU,)
        ))

        btn_h.btn(Button(
            ID=52, 
            x=pN_Cy(0.1), y=pN_Cy(0.38), width=pN_Cy(0.6), height=pN_Cy(0.05), 
            text="Quit", 
            button_type=ButtonType.DANGER, 
            callback=quit_game
        ))

    def draw_hud(self):
        gc: GameController = self.gc
        btn_h: ButtonsHandler = self.btn_h

        self.current_menu = gc.game_state

        if self.current_menu != self.last_menu:
            self.last_menu = self.current_menu
            btn_h.buttons = [None] * 100

        if self.current_menu == GameState.MENU:
            btn_h.menu_set(GameState.MENU)
            self.draw_menu_hud()

        elif self.current_menu == GameState.PLAYING:
            btn_h.menu_set(GameState.PLAYING)
            self.draw_playing_hud()

        elif self.current_menu == GameState.PAUSED:
            btn_h.menu_set(GameState.PAUSED)
            self.draw_paused_hud()
            
            

class ButtonType(Enum):
    REGULAR  = 0
    SUCCESS  = 1
    WARNING  = 2
    DANGER   = 3
    DISABLED = 4

    REGULAR_WIRE  = 5
    SUCCESS_WIRE  = 6
    WARNING_WIRE  = 7
    DANGER_WIRE   = 8
    DISABLED_WIRE = 9

class ButtonsHandler:
    def __init__(self, ui:UI):
        self.buttons: list[Button] = [None] * 100
        self.state: GameState = None

        self.ui: UI = ui

    def menu_set(self, state: GameState):
        self.state = state

    def btn(self, button: Button):
        self.buttons[button.ID] = button
        button.menu = self.state
        button.show()

    def click(self, x, y):
        for button in self.buttons:
            if button is None:
                continue
            if button.menu != self.state:
                continue

            if between(x, button.x, button.x + button.width) and between(y, button.y, button.y + button.height):
                self.ui.gc.mouse.left_button_pressed = False
                self.ui.gc.mouse.right_button_pressed = False
                button.click()
                return True

        return False

    def show(self):
        for button in self.buttons:
            if button is not None and button.menu == self.state:
                button.show()

    def remove_button(self, button: Button):
        self.buttons[button.ID] = None

class Button:
    def __init__(self, ID, x, y, width, height, text, button_type=ButtonType.REGULAR, callback = None, callback_args = None):
        self.ID = ID
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.button_type = button_type
        self.callback = callback
        self.callback_args = callback_args

        self.menu = None

    def get_color(self):
        if self.button_type in [ButtonType.SUCCESS, ButtonType.SUCCESS_WIRE]:
            return (0.15, 1.0, 0.25)
        elif self.button_type in [ButtonType.WARNING, ButtonType.WARNING_WIRE]:
            return (1.0, 1.0, 0.0)
        elif self.button_type in [ButtonType.DANGER, ButtonType.DANGER_WIRE]:
            return (1.0, 0.0, 0.0)
        elif self.button_type in [ButtonType.DISABLED, ButtonType.DISABLED_WIRE]:
            return (0.5, 0.5, 0.5)

        return (0.2, 0.2, 0.2)

    def show(self):
        glColor3f(*self.get_color())
        if self.button_type.value >= 5:
            glLineWidth(2.0)
            draw_rect_hollow(self.x, self.y, self.width, self.height)
        else:
            draw_rect(self.x, self.y, self.width, self.height)

        if self.button_type.value < 5:
            if self.button_type in (ButtonType.REGULAR, ButtonType.DISABLED):
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.0, 0.0, 0.0)
        else:
            glColor3f(*self.get_color())
        draw_text(self.x + self.width/2 - (len(self.text)*4), self.y + self.height/2 - 4, self.text)

    def click(self):
        if self.callback is not None:
            if self.callback_args is not None:
                self.callback(*self.callback_args)
            else:
                self.callback()