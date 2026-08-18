from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from utils import *
from enum import Enum

from particles import Particle, Particles

import math, random

_particles_manager : Particles = None

def set_particles_manager(particles_manager):
    global _particles_manager
    _particles_manager = particles_manager

class SHIP_TYPE(Enum):
    DESTROYER = 0
    BATTLESHIP = 1

g = 3.0
v = 40.0

class Bullets_Handler:
    def __init__(self):
        self.bullets = []

    def add_bullet(self, bullet):
        self.bullets.append(bullet)

    def update(self, dt):
        for i in range(len(self.bullets)- 1, -1, -1):
            self.bullets[i].update(dt)
            if self.bullets[i].position[2] < 0:
                global _particles_manager
                if _particles_manager is not None:
                    _particles_manager.add_particle_p(
                        position=[self.bullets[i].position[0], self.bullets[i].position[1], 0],
                        velocity=[0, 0, -1.0],
                        lifetime=random.uniform(1.0, 1.5),
                        size=random.uniform(2, 4),
                        color=(0.7, 1.0, 1.0)
                    )

                del self.bullets[i]

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()

class Bullet:
    def __init__(self, position):
        self.position = position

    def set_bullet_trajectory(self, target):
        position = self.position
        
        self.dir = [target[0] - position[0], target[1] - position[1]]

        d = math.sqrt(self.dir[0]**2 + self.dir[1]**2)
        h = position[2] - target[2]
        if d != 0:
            self.dir[0] /= d
            self.dir[1] /= d


        D = v**4 + 2* (v**2) * g * h - (g**2) * (d**2)
        if D >= 0:
            vf = d * math.sqrt( (v**2 + g*h + math.sqrt(D)) / (2 * (d**2 + h**2)) )
            vz = (g*d) / (2*vf) - (h*vf) / d

            self.velocity = [vf * self.dir[0], vf * self.dir[1], vz]

            return True
        return False

    def update(self, dt):
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt

        self.velocity[2] -= g * dt

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(1.0, 1.0, 0.0)
        glutSolidSphere(0.2, 10, 10)
        glPopMatrix()

class Ship:
    def __init__(self, ship_type, position, rotation):
        self.ship_type = ship_type
        self.position = position
        self.heading = rotation

        self.max_speed = 10.0 if ship_type == SHIP_TYPE.DESTROYER else 5.0
        self.acceleration = 2.0 if ship_type == SHIP_TYPE.DESTROYER else 1.0
        self.max_turning_speed = math.pi/4 if ship_type == SHIP_TYPE.DESTROYER else math.pi/8
        self.turning_acceleration = math.pi/8 if ship_type == SHIP_TYPE.DESTROYER else math.pi/16

        self.speed = 0.0
        self.turn = 0.0

        self.hp = 100 if ship_type == SHIP_TYPE.DESTROYER else 200
        self.damage = 10 if ship_type == SHIP_TYPE.DESTROYER else 20
        self.reload_time = 2.0 if ship_type == SHIP_TYPE.DESTROYER else 4.0

        self.load_status = 1.0
        
        self.throttle = 0.0
        self.steer = 0.0

        self.target = [0.0, 0.0, 0.0]

        self.turrets = []

        if ship_type == SHIP_TYPE.DESTROYER:
            self.turrets.append([2.0, 0.0, 0.75])
            self.turrets.append([-2.0, 0.0, 0.75])
        
    
    def move(self, throttle, steer, target):
        self.throttle = max(-1.0, min(1.0, throttle))
        self.steer = max(-1.0, min(1.0, steer))

        self.target[0] = target[0]
        self.target[1] = target[1]


    def update(self, dt):
        self.load_status += dt / self.reload_time
        self.load_status = min(self.load_status, 1.0)

        target_speed = self.throttle * self.max_speed
        target_turn = self.steer * self.max_turning_speed * (self.speed / self.max_speed)

        if self.speed < target_speed:
            self.speed += self.acceleration * dt
            if self.speed > target_speed:
                self.speed = target_speed
        elif self.speed > target_speed:
            self.speed -= self.acceleration * dt
            if self.speed < target_speed:
                self.speed = target_speed

        if self.turn < target_turn:
            self.turn += self.turning_acceleration * dt
            if self.turn > target_turn:
                self.turn = target_turn
        elif self.turn > target_turn:
            self.turn -= self.turning_acceleration * dt
            if self.turn < target_turn:
                self.turn = target_turn


        self.heading += self.turn * dt
        self.position[0] += self.speed * math.cos(self.heading) * dt
        self.position[1] += self.speed * math.sin(self.heading) * dt 

        global _particles_manager
        if _particles_manager is not None:
            if abs(self.speed) > 1:
                for _ in range(2):
                    x = random.uniform(-1.5, 1.5)
                    y = random.uniform(-1.5, 1.5)
                    particle_position = [self.position[0] + x, self.position[1] + y, 0]
                    particle_velocity = [0, 0, 0]

                    _particles_manager.add_particle_p(
                        position=particle_position, 
                        velocity=particle_velocity, 
                        lifetime=random.uniform(3.0, 7.0),
                        size=random.uniform(0.1, 0.5)
                    )


    def get_turret_pos(self):
        turret_positions = []
        for turret in self.turrets:
            turret_x = self.position[0] + turret[0] * math.cos(self.heading) - turret[1] * math.sin(self.heading)
            turret_y = self.position[1] + turret[0] * math.sin(self.heading) + turret[1] * math.cos(self.heading)
            turret_z = turret[2]
            turret_positions.append([turret_x, turret_y, turret_z])
        return turret_positions

    def draw_destroyer(self):
        glPushMatrix()
        glScalef(6.0, 1.5, 1.5)
        glColor3f(0.7, 0.7, 0.7)
        glutSolidCube(1.0)
        glPopMatrix()

        look = math.degrees(math.atan2(self.target[1] - self.position[1], self.target[0] - self.position[0]) - self.heading)

        for turret in self.turrets:
            glPushMatrix()
            glTranslatef(turret[0], turret[1], turret[2])
            glRotatef(look, 0, 0, 1)
            glScalef(0.6, 0.5, 0.5)
            glColor3f(0.2, 0.2, 0.2)
            glutSolidCube(1.0)
            glPopMatrix()

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], 0)
        glRotatef(math.degrees(self.heading), 0, 0, 1)
        if self.ship_type == SHIP_TYPE.DESTROYER:
            self.draw_destroyer()
        elif self.ship_type == SHIP_TYPE.BATTLESHIP:
            glPushMatrix()
            glScalef(10.0, 2.0, 1.5)
            glColor3f(1.0, 0.5, 0.5)
            glutSolidCube(2.0)
            glPopMatrix()
        glPopMatrix()




class Player:
    def __init__(self, position, rotation):
        self.ship = Ship(SHIP_TYPE.DESTROYER, position, rotation)

    def update(self, thr, steer, target, dt):
        self.ship.move(thr, steer, target)
        self.ship.update(dt)

    def draw(self):
        self.ship.draw()