from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from math import sin, cos, pi, radians, degrees

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