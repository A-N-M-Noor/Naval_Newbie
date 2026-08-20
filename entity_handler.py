from __future__ import annotations

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from utils import *
from enum import Enum

from particles import Particle, Particles

import math, random

_particles_manager : Particles = None
_bullets_manager : Bullets_Handler = None
_ships_handler : Ships_Handler = None
_islands: list[Island] = []

def set_particles_manager(particles_manager):
    global _particles_manager
    _particles_manager = particles_manager

def set_bullets_manager(bullets_manager):
    global _bullets_manager
    _bullets_manager = bullets_manager

def set_islands(islands):
    global _islands
    _islands = islands

def set_ships_handler(ships_handler):
    global _ships_handler
    _ships_handler = ships_handler

class SubIsland:
    def __init__(self, position, size):
        self.position = position
        self.size = size
        self.color = (random.uniform(0.2, 0.4), random.uniform(0.6, 0.9), random.uniform(0.2, 0.4))

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(*self.color)
        glutSolidSphere(self.size/2, 20, 20)
        glPopMatrix()

class Island:
    def __init__(self, position, size, sub_count):
        self.position = position
        self.size = size
        self.sub_count = sub_count

        self.sub_islands = []

        for _ in range(sub_count):
            sub_size = random.uniform(0.35, 0.6) * size
            ang = random.uniform(0, 2 * math.pi)
            d = (size - sub_size)/2

            sub_x = position[0] + d * math.cos(ang)
            sub_y = position[1] + d * math.sin(ang)
            self.sub_islands.append(SubIsland(position=(sub_x, sub_y, -sub_size/4), size=sub_size))

    def draw(self):
        for sub_island in self.sub_islands:
            sub_island.draw()      

class SHIP_TYPE(Enum):
    DESTROYER = 0
    BATTLESHIP = 1

g = 1.0
v = 40.0

class Bullets_Handler:
    def __init__(self):
        self.bullets = []

    def add_bullet(self, bullet):
        self.bullets.append(bullet)


    def update(self, dt):
        global _particles_manager

        for i in range(len(self.bullets)- 1, -1, -1):
            bullet: Bullet = self.bullets[i]

            bullet.update(dt)
            if bullet.position[2] <= 0:
                if _particles_manager is not None:
                    _particles_manager.add_particle_p(
                        position=[bullet.position[0], bullet.position[1], 0],
                        velocity=[0, 0, -1.0],
                        lifetime=random.uniform(1.0, 1.5),
                        size=random.uniform(2, 4),
                        color=(0.7, 1.0, 1.0)
                    )

                del self.bullets[i]
                continue

            if bullet.position[2] < 20: #island level 
                global _islands
                deleted = False
                for island in _islands:
                    if bullet.collide_island(island):
                        if _particles_manager is not None:
                            _particles_manager.add_particle_p(
                                position=[bullet.position[0], bullet.position[1], bullet.position[2]],
                                velocity=[0, 0, 0.0],
                                lifetime=random.uniform(1.0, 1.5),
                                size=random.uniform(2, 4),
                                color=(1.0, random.uniform(0.7, 0.8), random.uniform(0.20, 0.40))
                            )
                        deleted = True
                        break
                if deleted:
                    del self.bullets[i]
                    continue

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()

class Bullet:
    def __init__(self, position, damage = 10, player_bullet = True):
        self.position = position
        self.player_bullet = player_bullet
        self.damage = 10

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

    def is_col_island(self, island: Island):
            for sub_island in island.sub_islands:
                if dist_3D(self.position, sub_island.position) < (sub_island.size/2):
                    dir = [self.position[0] - sub_island.position[0], self.position[1] - sub_island.position[1], self.position[2] - sub_island.position[2]]
                    dir = set_mag(dir, sub_island.size/2)
                    self.position[0] = sub_island.position[0] + dir[0]
                    self.position[1] = sub_island.position[1] + dir[1]
                    self.position[2] = sub_island.position[2] + dir[2]
                    return True
            return False
    
    def collide_island(self, island: Island):
        if cube_collide(self.position, island.position, island.size*2):
            col = self.is_col_island(island)
            if col:
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
        self.last_position = position.copy()
        self.heading = rotation
        self.last_heading = rotation

        self.max_speed = 10.0 if ship_type == SHIP_TYPE.DESTROYER else 5.0
        self.acceleration = 2.0 if ship_type == SHIP_TYPE.DESTROYER else 1.0
        self.max_turning_speed = math.pi/4 if ship_type == SHIP_TYPE.DESTROYER else math.pi/8
        self.turning_acceleration = math.pi/8 if ship_type == SHIP_TYPE.DESTROYER else math.pi/16

        self.speed = 0.0
        self.turn = 0.0

        self.max_hp = 100 if ship_type == SHIP_TYPE.DESTROYER else 200
        self.hp = self.max_hp
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

    def add_bubbles(self, pos, spread, init_size=0.5, quantity=3):
        for _ in range(quantity):
            x = random.uniform(-spread, spread)
            y = random.uniform(-1.5, 1.5)
            particle_position = [pos[0] + x, pos[1] + y, 0]
            particle_velocity = [0, 0, 0]

            _particles_manager.add_particle_p(
                position=particle_position, 
                velocity=particle_velocity, 
                lifetime=random.uniform(3.0, 7.0),
                size=random.uniform(init_size/5.0, init_size)
            )

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

        self.last_position = self.position.copy()
        self.last_heading = self.heading

        self.heading += self.turn * dt
        self.position[0] += self.speed * math.cos(self.heading) * dt
        self.position[1] += self.speed * math.sin(self.heading) * dt 

        global _particles_manager
        if _particles_manager is not None:
            d = dist_2D(self.last_position, self.position)
            if d > 0:
                t = 0
                while t < 1:
                    t += 1/d
                    p = lerp_nD(self.last_position, self.position, t)
                    self.add_bubbles(p, 1.5, 0.5*(self.speed / self.max_speed), 3)

        for island in _islands:
            if rect_collide(self.position, island.position, island.size*2):
                if dist_2D(self.position, island.position) < island.size/2:
                    dir = [self.position[0] - island.position[0], self.position[1] - island.position[1], 0]
                    dir = set_mag(dir, island.size/2)
                    self.position[0] = island.position[0] + dir[0]
                    self.position[1] = island.position[1] + dir[1]

                    self.speed *= 0.5

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

class Ships_Handler:
    def __init__(self):
        self.ships = []

    def add_ship(self, ship):
        self.ships.append(ship)

    def update(self, player_ship, dt):
        for ship in self.ships:
            ship.update(dt)

    def draw(self):
        for ship in self.ships:
            ship.draw()



class Player:
    def __init__(self, position, rotation):
        self.ship = Ship(SHIP_TYPE.DESTROYER, position, rotation)

    def update(self, thr, steer, target, dt):
        self.ship.move(thr, steer, target)
        self.ship.update(dt)

    def draw(self):
        self.ship.draw()