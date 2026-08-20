from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import time

import pyautogui

class KeyboardInput:
    def __init__(self):
        self.keys_pressed = set()
        self.special_keys_pressed = set()

        self.key_callback = None

    def key_pressed(self, key, x, y):
        if self.key_callback is not None:
            self.key_callback(key, False)
        self.keys_pressed.add(key)

    def key_released(self, key, x, y):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def special_key_pressed(self, key, x, y):
        if self.key_callback is not None:
            self.key_callback(key, True)
        self.special_keys_pressed.add(key)

    def special_key_released(self, key, x, y):
        if key in self.special_keys_pressed:
            self.special_keys_pressed.remove(key)
    
    def isPressed(self, key):
        return key in self.keys_pressed

class MouseInput:
    def __init__(self):
        self.mouse_position = (0, 0)
        self.mouse_callback = None
        self.mouse_wheel_callback = None

        self.left_button_pressed = False
        self.right_button_pressed = False

        self.left_clicked = False
        self.left_click_time = 0.0

        self.right_clicked = False
        self.right_click_time = 0.0

    def is_right_clicked(self):
        if self.right_clicked and (time.time() - self.right_click_time) < 0.5:
            self.right_clicked = False
            return True
        self.right_clicked = False
        return False

    def is_left_clicked(self):
        if self.left_clicked and (time.time() - self.left_click_time) < 0.5:
            self.left_clicked = False
            return True
        self.left_clicked = False
        return False

    def mouse_click(self, button, state, x, y):
        if self.mouse_callback is not None:
            if button == GLUT_LEFT_BUTTON:
                self.mouse_callback(True, state == GLUT_DOWN)
                self.left_button_pressed = state == GLUT_DOWN

                if state == GLUT_DOWN:
                    self.left_clicked = True
                    self.left_click_time = time.time()
            elif button == GLUT_RIGHT_BUTTON:
                self.mouse_callback(False, state == GLUT_DOWN)
                self.right_button_pressed = state == GLUT_DOWN

                if state == GLUT_DOWN:
                    self.right_clicked = True
                    self.right_click_time = time.time()

            elif button == 3:  # Scroll up
                if self.mouse_wheel_callback is not None:
                    self.mouse_wheel_callback(1)
            elif button == 4:  # Scroll down
                if self.mouse_wheel_callback is not None:
                    self.mouse_wheel_callback(-1)

            

    def mouse_wheel(self, wheel, direction, x, y):
        print(f"Mouse wheel scrolled {'up' if direction > 0 else 'down'} at position ({x}, {y})")
        if self.mouse_wheel_callback is not None:
            self.mouse_wheel_callback(direction)

    def mouse_move(self, x, y):
        self.mouse_position = (x, y)

    def set_pos(self, x, y):
        if pyautogui is None:
            raise RuntimeError("pyautogui is required for MouseInput.set_pos")
        wX, wY = glutGet(GLUT_WINDOW_X), glutGet(GLUT_WINDOW_Y)
        pyautogui.moveTo(wX + x, wY + y)

    def get_pos(self):
        return self.mouse_position