from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Particle:
    def __init__(self, position, velocity, lifetime, size=1.0, color=(1.0, 1.0, 1.0)):
        self.position = position
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0.0
        self.size = size
        self.color = color

    def update(self, dt):
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt
        self.age += dt

    def sz(self):
        t = self.age / self.lifetime
        s = -(1.5*t - 0.5)**2 +1.0
        return self.size * s

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(*self.color)
        glutSolidSphere(self.sz(), 10, 10)
        glPopMatrix()
    
    def is_alive(self):
        return self.age < self.lifetime

class Particles:
    def __init__(self):
        self.particles = []

    def add_particle(self, particle):
        self.particles.append(particle)

    def add_particle_p(self, position, velocity, lifetime, size=1.0, color=(1.0, 1.0, 1.0)):
        particle = Particle(position, velocity, lifetime, size, color)
        self.particles.append(particle)

    def update(self, dt):
        for i in range(len(self.particles)- 1, -1, -1):
            self.particles[i].update(dt)
            if not self.particles[i].is_alive():
                del self.particles[i]

    def draw(self):
        for particle in self.particles:
            particle.draw()