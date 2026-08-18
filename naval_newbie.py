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
from entity_handler import Ship, SHIP_TYPE, Player, Bullet, Bullets_Handler, set_particles_manager
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

        self.particle_manager = Particles()
        set_particles_manager(self.particle_manager)

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

    def handle_click(self, is_left_button, is_pressed):
        if is_pressed:
            print(f"Mouse button {'left' if is_left_button else 'right'} pressed")
        else:
            print(f"Mouse button {'left' if is_left_button else 'right'} released")

    def handle_scroll(self, direction):
        if self.game_state == GameState.PLAYING:
            if direction > 0:
                self.cam.zoom_camera(-0.5)
            else:
                self.cam.zoom_camera(0.5)

    
    def draw_hud(self):
        draw_text(10, self.HEIGHT - 30, f"Game State: {self.game_state.name}")

        if self.game_state == GameState.PLAYING:
            l = self.player.ship.load_status * 90
            glColor3f(0.0, 0.0, 0.0)
            glLineWidth(4.0)
            draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), 135, 225, segments=25)
            draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), -45, 45, segments=25)

            glLineWidth(2.0)
            glColor3f(0.0, 1.0, 0.0)
            draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), 225-l, 225, segments=25)
            draw_arc(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.05), -45, -45+l, segments=25)

            glColor3f(0.2, 0.2, 0.2)
            draw_circle(pN_Cx(0.5), pN_Cy(0.5), pN_Cy(0.01), segments=10)

            draw_line(pN_Cx(0.55), pN_Cy(0.5), pN_Cx(0.9), pN_Cy(0.5))
            draw_line(pN_Cx(0.45), pN_Cy(0.5), pN_Cx(0.1), pN_Cy(0.5))

            for i in range(10):
                        x = 0.55 + i* ((0.9-0.55)/10)
                        draw_line(pN_Cx(x), pN_Cy(0.495), pN_Cx(x), pN_Cy(0.505))

                        x = 0.45 + i* ((0.1-0.45)/10)
                        draw_line(pN_Cx(x), pN_Cy(0.495), pN_Cx(x), pN_Cy(0.505))

    def showScreen(self):
        glClearColor(0.5, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.WIDTH, self.HEIGHT)

        set_window_size(self.WIDTH, self.HEIGHT)
        
        self.cam.setupCamera()

        if self.game_state in (GameState.PLAYING, GameState.PAUSED):
            glBegin(GL_QUADS)
            glColor3f(0, 0.75, 1)
            glVertex3f(-1000, -1000, 0)
            glVertex3f(-1000, 1000, 0)
            glVertex3f(1000, 1000, 0)
            glVertex3f(1000, -1000, 0)
            glEnd()

        self.target_3D = self.cam.get_target_pos(h=0.0)
        glPushMatrix()
        glTranslatef(self.target_3D[0], self.target_3D[1], self.target_3D[2])
        glColor3f(1.0, 0.0, 0.0)
        glutSolidSphere(0.1, 20, 20)
        glPopMatrix()

        self.player.draw()
        self.particle_manager.draw()
        self.bullets_manager.draw()

        begin2D(self.WIDTH, self.HEIGHT)
        self.draw_hud()
        end2D()

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

    def idle(self):
        current_time = time.time()
        self.dt = current_time - self.last_frame_time
        self.last_frame_time = current_time

        self.WIDTH, self.HEIGHT = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)

        if self.game_state == GameState.PLAYING:
            self.cam.update_cam(cam_target=[self.player.ship.position[0], self.player.ship.position[1], 2.0])
            cP = self.mouse.get_pos()
            cD = (cP[0] - self.WIDTH//2, cP[1] - self.HEIGHT//2)
            if cD[0] != 0 or cD[1] != 0:
                self.cam.move_camera(cursor_dir=cD, scale=(-0.01, 0.01), dt=self.dt)
            self.mouse.set_pos(self.WIDTH//2, self.HEIGHT//2)

            self.particle_manager.update(self.dt)

            self.player_control()

            if(self.mouse.left_button_pressed and self.player.ship.load_status >= 1.0):
                turrets = self.player.ship.get_turret_pos()
                for turret in turrets:
                    bullet = Bullet(position=turret.copy())
                    spread = 0.5
                    tg = [self.target_3D[0] + random.uniform(-spread, spread), self.target_3D[1] + random.uniform(-spread, spread), self.target_3D[2]]
                    if bullet.set_bullet_trajectory(target=tg):
                        self.bullets_manager.add_bullet(bullet)
                self.player.ship.load_status = 0.0

            self.bullets_manager.update(self.dt)

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