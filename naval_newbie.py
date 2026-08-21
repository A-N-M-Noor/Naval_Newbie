import time
import math, random
import numpy as np
from enum import Enum

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from utils import *
from inputs_handler import KeyboardInput, MouseInput
from camera_controller import CameraController
from entity_handler import Ship, Ships_Handler, SHIP_TYPE, Player, Bullet, Bullets_Handler, Island
from entity_handler import set_ships_handler, set_particles_manager, set_bullets_manager, set_islands
from particles import Particle, Particles

from enum import Enum

class GameState(Enum):
    MENU = 0
    UPGRADES = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

class GameController:
    def __init__(self):
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.cursor_hidden = False

        self.keyboard = KeyboardInput()
        self.keyboard.key_callback = self.handle_key

        self.mouse = MouseInput()
        self.mouse.mouse_callback = self.handle_click
        self.mouse.mouse_wheel_callback = self.handle_scroll

        self.cam = CameraController(fovY=90)

        self.last_frame_time = time.time()
        self.dt = 0

        self.game_state = GameState.PLAYING


        self.player = Player(position=[0, 0], rotation=0)
        self.target_3D = [0.0, 0.0, 0.0]

        self.bullets_manager = Bullets_Handler()
        set_bullets_manager(self.bullets_manager)

        self.particle_manager = Particles()
        set_particles_manager(self.particle_manager)

        self.islands = []
        set_islands(self.islands)
        self.set_environment()

        self.ships_handler = Ships_Handler()
        set_ships_handler(self.ships_handler)

        for _ in range(2):
            self.add_ship()


    def add_ship(self):
        while True:
            dir = random.uniform(0, 2*math.pi)
            dst = random.uniform(300, 600)
            x = self.player.ship.position[0] + dst * math.cos(dir)
            y = self.player.ship.position[1] + dst * math.sin(dir)

            if not between(x, -500, 500) or not between(y, -500, 500):
                continue

            for ship in self.ships_handler.ships:
                if dist_2D([x, y], ship.position) < 300:
                    continue
            
            col = False
            for island in self.islands:
                if dist_2D([x, y], island.position) < island.size + 100:
                    col = True
                    break
            if not col:
                s_type = random.random()
                if s_type < 0.5:
                    s_type = SHIP_TYPE.DESTROYER
                else:
                    s_type = SHIP_TYPE.BATTLESHIP

                ship = Ship(position=[x, y], rotation=random.uniform(0, math.pi * 2), ship_type=s_type)
                print(f"Added ship type of {ship.ship_type.name}")
                self.ships_handler.add_ship(ship)
                break

    def set_environment(self):
        island_count = random.randint(20, 30)
        for _ in range(island_count):
            pos = [random.uniform(-500, 500), random.uniform(-500, 500), 0]
            size = random.uniform(50, 60)
            sub_count = random.randint(8, 16)
            island = Island(position=pos, size=size, sub_count=sub_count)
            self.islands.append(island)

    def set_cursor_hidden(self, hidden):
        self.cursor_hidden = hidden
        if hidden:
            glutSetCursor(GLUT_CURSOR_NONE)
        else:
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)

    def is_cursor_hidden(self):
        return self.cursor_hidden

    def sync_cursor_visibility(self):
        self.set_cursor_hidden(self.game_state == GameState.PLAYING)

    def handle_key(self, key, is_special):
        if is_special:
            pass
        else:
            if key == b'p':
                if self.game_state == GameState.PLAYING:
                    self.game_state = GameState.PAUSED
                elif self.game_state == GameState.PAUSED:
                    self.mouse.set_pos(self.WIDTH//2, self.HEIGHT//2)
                    self.game_state = GameState.PLAYING
                self.sync_cursor_visibility()

            if key == b'z':
                if self.cam.fovY == 90:
                    self.cam.fovY = 15
                else:
                    self.cam.fovY = 90

    def handle_click(self, button, is_pressed):
        if is_pressed and button == GLUT_LEFT_BUTTON:
            self.shoot_bullet()
        elif is_pressed and button == GLUT_RIGHT_BUTTON:
            self.shoot_torpedo()

    def handle_scroll(self, direction):
        if self.game_state == GameState.PLAYING:
            if direction > 0:
                self.cam.zoom_camera(-0.5)
            else:
                self.cam.zoom_camera(0.5)

    def draw_ship_marker(self, ship: Ship):
        marker_p = [ship.position[0], ship.position[1], ship.size[2] + 1.0]
        pos_x, pos_y, visible = conv_3d_2_2d(marker_p, self.cam)

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
        ms = pN_Cy(0.3)
        map_size = 600

        return remap(x, -map_size, map_size, self.WIDTH - ms, self.WIDTH)

    def mm_y(self, y):
        ms = pN_Cy(0.3)
        map_size = 600

        return remap(y, -map_size, map_size, 0, ms)

    def draw_minimap(self):
        ms = pN_Cy(0.3)
        map_size = 600
        
        glLineWidth(2.0)
        glColor3f(0.2, 0.9, 0.9)
        draw_rect(
            self.WIDTH - ms, 0, ms, ms 
        )
        glColor3f(0.0, 0.0, 0.0)
        draw_rect_hollow(
            self.WIDTH - ms, 0, ms, ms 
        )

        for island in self.islands:
            for sub in island.sub_islands:
                x = self.mm_x(sub.position[0])
                y = self.mm_y(sub.position[1])
                glColor3f(sub.color[0], sub.color[1], sub.color[2])
                draw_filled_circle(x, y, remap(sub.size, 0, map_size*2, 0, ms/2), segments=10)

        for ship in self.ships_handler.ships:
            x = self.mm_x(ship.position[0])
            y = self.mm_y(ship.position[1])
            if ship.ship_type == SHIP_TYPE.DESTROYER:
                glColor3f(1.0, 0.5, 0.0)
            else:
                glColor3f(1.0, 0.0, 0.5)
            draw_rect(x, y, pN_Cy(0.015), pN_Cy(0.0075), ship.heading)

        x = self.mm_x(self.player.ship.position[0])
        y = self.mm_y(self.player.ship.position[1])
        glColor3f(0.0, 0.0, 1.0)
        draw_rect(x, y, pN_Cy(0.015), pN_Cy(0.0075), self.player.ship.heading)

        t_x = self.mm_x(self.target_3D[0])
        t_y = self.mm_y(self.target_3D[1])

        t_x = clamp(t_x, self.WIDTH - ms, self.WIDTH)
        t_y = clamp(t_y, 0, ms)

        glColor3f(1.0, 1.0, 0.0)
        draw_line(t_x, t_y+5, t_x, t_y-5)
        draw_line(t_x+5, t_y, t_x-5, t_y)

    def draw_ship_healtbar(self):
        w = self.WIDTH - pN_Cy(0.7)
        h = pN_Cy(0.06)
        x = self.WIDTH/2 - w/2
        y = pN_Cy(0.05)

        glColor3f(0.2, 0.2, 0.2)
        draw_rect(x-2, y-2, w+4, h+4)
        glColor3f(0.15, 1.0, 0.25)
        ht = self.player.ship.hp / self.player.ship.max_hp
        if ht > 0.0:
            draw_rect(x, y, w * ht, h)

    def draw_playing_hud(self):
        l = self.player.ship.load_status * 90
        l_t = self.player.ship.torpedo_load_status * 90
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

        for ship in self.ships_handler.ships:
            self.draw_ship_marker(ship)

        self.draw_minimap()

        self.draw_ship_healtbar()


    def draw_hud(self):
        draw_text(10, self.HEIGHT - 30, f"Game State: {self.game_state.name}")

        if self.game_state == GameState.PLAYING:
            self.draw_playing_hud()

        if self.game_state == GameState.PAUSED:
            pass

    def get_target_3D(self):
        t_3D = self.cam.get_target_pos(h=0.0)

        for ship in self.ships_handler.ships:
            p = line_intersect_box_r(ship.position, scale_nD(ship.size, [4, 3.0, 6.0]), ship.heading, self.cam.position, t_3D, output_both=True)
            if p:
                p1 = p[0]
                p2 = p[1]
                if p1 and p2:
                    p = [(p1[0] + p2[0])/2, (p1[1] + p2[1])/2, (p1[2] + p2[2])/2]
                    return p
                return p1

        return t_3D

    def show_game(self):
        self.cam.setupCamera()
        
        if self.game_state in (GameState.PLAYING, GameState.PAUSED):
            glBegin(GL_QUADS)
            glColor3f(0, 0.75, 1)
            glVertex3f(-1000, -1000, 0)
            glVertex3f(-1000, 1000, 0)
            glVertex3f(1000, 1000, 0)
            glVertex3f(1000, -1000, 0)
            glEnd()

        self.target_3D = self.get_target_3D()

        glPushMatrix()
        glTranslatef(self.target_3D[0], self.target_3D[1], self.target_3D[2])
        glColor3f(1.0, 0.0, 0.0)
        glutSolidSphere(0.1, 10, 10)
        glPopMatrix()
        
        self.player.draw()
        self.ships_handler.draw()
        self.particle_manager.draw()
        self.bullets_manager.draw()

        for island in self.islands:
            island.draw()

        begin2D(self.WIDTH, self.HEIGHT)
        self.draw_hud()
        end2D()

    def showScreen(self):
        glClearColor(0.5, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.WIDTH, self.HEIGHT)

        set_window_size(self.WIDTH, self.HEIGHT)
        
        if self.game_state in (GameState.PLAYING, GameState.PAUSED):
            self.show_game()

        glutSwapBuffers()

    def player_control(self):
        thr = 0.0
        if self.keyboard.isPressed(b'w'):
            thr += 1.0
        if self.keyboard.isPressed(b's'):
            thr -= 1.0

        ster = 0.0
        if self.keyboard.isPressed(b'a'):
            ster += 1.0
        if self.keyboard.isPressed(b'd'):
            ster -= 1.0

        self.player.update(thr, ster, self.target_3D, self.dt)   

    def shoot_bullet(self):
        if self.player.ship.load_status < 1.0:
            return
        turrets = self.player.ship.get_turret_pos()
        for turret in turrets:
            bullet = Bullet(position=turret.copy(), damage=self.player.ship.damage, player_bullet=True)
            spread = 0.25
            tg = [self.target_3D[0] + random.uniform(-spread, spread), self.target_3D[1] + random.uniform(-spread, spread), 0.0]
            if bullet.set_bullet_trajectory(target=tg):
                self.bullets_manager.add_bullet(bullet)
        self.player.ship.load_status = 0.0

    def shoot_torpedo(self):
        if self.player.ship.torpedo_load_status < 1.0:
            return
        bullet = Bullet(position=self.player.ship.position.copy(), damage=self.player.ship.damage, player_bullet=True)
        if bullet.set_torpedo_trajectory(target=self.target_3D):
            self.bullets_manager.add_bullet(bullet)
        self.player.ship.torpedo_load_status = 0.0

    
    def game_play_update(self):
        if len(self.ships_handler.ships) < 2:
            self.add_ship()

        self.cam.update_cam(cam_target=[self.player.ship.position[0], self.player.ship.position[1], 2.0])
        cP = self.mouse.get_pos()
        cD = (cP[0] - self.WIDTH//2, cP[1] - self.HEIGHT//2)
        if cD[0] != 0 or cD[1] != 0:
            self.cam.move_camera(cursor_dir=cD, scale=(-0.01, 0.01), dt=self.dt)
        self.mouse.set_pos(self.WIDTH//2, self.HEIGHT//2)

        self.particle_manager.update(self.dt)

        self.player_control()
        self.ships_handler.update(self.player.ship, self.dt)

        if(self.mouse.left_button_pressed):
            self.shoot_bullet()

        if(self.mouse.right_button_pressed):
            self.shoot_torpedo()

        self.bullets_manager.update(self.player.ship, self.dt)

    def idle(self):
        current_time = time.time()
        self.dt = current_time - self.last_frame_time
        self.last_frame_time = current_time

        self.WIDTH, self.HEIGHT = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)

        if self.game_state == GameState.PLAYING:
            self.game_play_update()

        glutPostRedisplay()

    def main(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.WIDTH, self.HEIGHT)
        glutInitWindowPosition(0, 0)
        wind = glutCreateWindow(b"3D OpenGL Intro")

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glClearDepth(1.0)
        self.sync_cursor_visibility()

        glutDisplayFunc(self.showScreen)
        glutKeyboardFunc(self.keyboard.key_pressed)
        glutKeyboardUpFunc(self.keyboard.key_released)
        glutSpecialFunc(self.keyboard.special_key_pressed)
        glutSpecialUpFunc(self.keyboard.special_key_released)
        glutMouseFunc(self.mouse.mouse_click)
        glutPassiveMotionFunc(self.mouse.mouse_move)
        glutMotionFunc(self.mouse.mouse_move)
        glutIdleFunc(self.idle)

        glutMainLoop()

if __name__ == "__main__":
    game = GameController()
    game.main()