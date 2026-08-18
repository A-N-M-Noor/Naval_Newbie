from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import numpy as np

from utils import lerp

class CameraController:
    def __init__(self, fovY):
        self.distance = 5.0
        self.yaw = 0.0
        self.pitch = np.deg2rad(30.0)
        self.z = 10.0
        self.position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        self.up = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        self.fovY = fovY

        self.dt = 0.0

    def move_camera(self, cursor_dir, scale, dt):
        self.dt = dt
        self.pitch += cursor_dir[1] * scale[1] * dt
        self.yaw += cursor_dir[0] * scale[0] * dt

        self.pitch = min(max(self.pitch, np.deg2rad(0.5)), np.deg2rad(20))

    def zoom_camera(self, zoom_amount):
        self.distance += zoom_amount
        self.distance = min(max(self.distance, 5.0), 15.0)
        
    def update_cam(self, cam_target):
        self.target[0] = cam_target[0]
        self.target[1] = cam_target[1]
        self.target[2] = cam_target[2]

    def setupCamera(self):
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(self.fovY, width/height, 0.1, 5000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        d = self.distance

        if(self.fovY < 60):
            d = 5.0

        b = d * np.cos(self.pitch)
        h = d * np.sin(self.pitch)

        x = b * np.cos(self.yaw)
        y = b * np.sin(self.yaw)


        self.position[0] = lerp(self.position[0], self.target[0] + x, 5 * self.dt)
        self.position[1] = lerp(self.position[1], self.target[1] + y, 5 * self.dt)
        self.position[2] = lerp(self.position[2], self.target[2] + h, 5 * self.dt)

        gluLookAt(self.position[0], self.position[1], self.position[2],
                self.target[0], self.target[1], self.target[2],
                self.up[0], self.up[1], self.up[2])

    def get_target_pos(self, h = 0.0):
        t = (h - self.position[2]) / (self.target[2] - self.position[2])

        x = self.position[0] + t * (self.target[0] - self.position[0])
        y = self.position[1] + t * (self.target[1] - self.position[1])
        z = h

        return x, y, z
