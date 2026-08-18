from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from math import sin, cos, pi, radians, degrees, sqrt

import numpy as np

_W, _H = 1000, 700


def set_window_size(width, height):
    global _W, _H
    _W, _H = width, height


def pN_Cx(x):
    return (x * _W)
def pN_Cy(y):
    return (y * _H)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_arc(x, y, radius, start_angle, end_angle, segments=100):
    start_angle = radians(start_angle)
    end_angle = radians(end_angle)

    glBegin(GL_LINE_STRIP)
    for i in range(segments + 1):
        angle = start_angle + (end_angle - start_angle) * (i / segments)
        glVertex2f(x + radius * cos(angle), y + radius * sin(angle))
    glEnd()

def draw_circle(x, y, radius, segments=100):
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        angle = 2 * pi * (i / segments)
        glVertex2f(x + radius * cos(angle), y + radius * sin(angle))
    glEnd()

def draw_line(x1, y1, x2, y2):
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_triangle(x1, y1, x2, y2, x3, y3):
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()

def begin2D(WIDTH, HEIGHT):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

def end2D():
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_rect(x, y, w, h):
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

def lerp(a, b, t):
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return a + (b - a) * t

def between(v, a, b):
    return v >= a and v <= b

def cube_collide(pos1: list[float], pos2: list[float], size: list[float] | float) -> bool:
    x, y, z = pos1
    x2, y2, z2 = pos2

    if isinstance(size, (int, float)):
        sx = sy = sz = size / 2
    else:
        sx, sy, sz = size
    sx, sy, sz = sx/2, sy/2, sz/2

    return between(x, x2-sx, x2+sx) and between(y, y2-sy, y2+sy) and between(z, z2-sz, z2+sz)

def rect_collide(pos1: list[float], pos2: list[float], size: list[float] | float) -> bool:
    x, y = pos1[0], pos1[1]
    x2, y2 = pos2[0], pos2[1]

    if isinstance(size, (int, float)):
        sx = sy = size / 2
    else:
        sx, sy = size[0], size[1]
    sx, sy = sx/2, sy/2

    return between(x, x2-sx, x2+sx) and between(y, y2-sy, y2+sy)

def dist_3D(p1: list[float], p2: list[float]) -> float:
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

def dist_2D(p1: list[float], p2: list[float]) -> float:
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def set_mag(vec: list[float], mag: float) -> list[float]:
    x, y, z = vec
    current_mag = sqrt(x**2 + y**2 + z**2)
    if current_mag == 0:
        return [0, 0, 0]
    scale = mag / current_mag
    return [x * scale, y * scale, z * scale]

def conv_3d_2_2d(pos_3d: list[float], cam) -> tuple[float, float, bool]:
    if len(pos_3d) == 2:
        pos_3d = [pos_3d[0], pos_3d[1], 0.0]

    width = float(_W)
    height = float(_H)
    aspect = width / height if height != 0 else 1.0

    camera_pos = np.array(cam.position, dtype=float)
    camera_target = np.array(cam.target, dtype=float)
    camera_up = np.array(cam.up, dtype=float)

    forward = camera_target - camera_pos
    forward_norm = np.linalg.norm(forward)
    if forward_norm == 0:
        return 0.0, 0.0, False
    forward = forward / forward_norm

    right = np.cross(forward, camera_up)
    right_norm = np.linalg.norm(right)
    if right_norm == 0:
        right = np.array([1.0, 0.0, 0.0], dtype=float)
    else:
        right = right / right_norm

    true_up = np.cross(right, forward)

    rel = np.array(pos_3d, dtype=float) - camera_pos

    x_cam = float(np.dot(rel, right))
    y_cam = float(np.dot(rel, true_up))
    z_cam = float(np.dot(rel, forward))

    if z_cam <= 1e-6:
        return 0.0, 0.0, False

    half_fov = radians(float(cam.fovY) * 0.5)
    sin_half = sin(half_fov)
    focal = cos(half_fov) / sin_half if sin_half != 0 else 1.0

    x_ndc = (x_cam / z_cam) * (focal / aspect)
    y_ndc = (y_cam / z_cam) * focal

    screen_x = (x_ndc + 1.0) * 0.5 * width
    screen_y = (y_ndc + 1.0) * 0.5 * height

    return screen_x, screen_y, True


    