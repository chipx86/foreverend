import math
import random

import pygame
from pygame.locals import *

from foreverend.resources import load_image
from foreverend.timer import Timer


class Particle(object):
    def __init__(self, system):
        self.system = system
        self.pos = (0, 0)
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.lifetime = 0.0
        self.elapsed_time = 0.0
        self.rotation = 0
        self.rotation_speed = 0
        self.scale = 0

    @property
    def active(self):
        return self.elapsed_time < self.lifetime

    def update(self, dt):
        self.velocity = (self.velocity[0] + self.acceleration[0] * dt,
                         self.velocity[1] + self.acceleration[1] * dt)
        self.pos = (int(self.pos[0] + self.velocity[0] * dt),
                    int(self.pos[1] + self.velocity[1] * dt))
        self.rotation += self.rotation_speed * dt
        self.elapsed_time += dt

    def draw(self, surface):
        norm_lifetime = self.elapsed_time / self.lifetime
        scale = self.scale * (0.75 + 0.25 * norm_lifetime)
        image = pygame.transform.rotozoom(self.system.image, self.rotation, scale)
        #alpha = 255.0 * (4 * norm_lifetime * (1 - norm_lifetime))

        surface.blit(image, self.pos)


class ParticleSystem(object):
    def __init__(self, time_period, max_particles):
        # Settings
        self.particle_filename = None
        self.min_particles = 0
        self.max_particles = max_particles
        self.min_initial_speed = 0
        self.max_initial_speed = 0
        self.min_acceleration = 0
        self.max_acceleration = 0
        self.min_lifetime = 0
        self.max_lifetime = 0
        self.min_scale = 0
        self.max_scale = 0
        self.min_rotation_speed = 0
        self.max_rotation_speed = 0
        self.repeat = False

        # State
        self.time_period = time_period
        self.image = None
        self.particles = []
        self.free_particles = []
        self.pos = None

        self.timer = Timer(60, self.on_particle_update)

    def start(self, x, y):
        assert self.pos is None
        self.pos = (x, y)

        self.particles = []

        for i in range(self.max_particles):
            self.particles.append(Particle(self))

        self.free_particles = list(self.particles)

        if not self.image:
            self.image = load_image(self.particle_filename).convert_alpha()

        self.add_particles()

    def add_particles(self):
        num_particles = random.randint(self.min_particles, self.max_particles)

        for i in range(num_particles):
            if self.free_particles:
                self.setup_particle(self.free_particles.pop())

        self.time_period.particle_systems.append(self)
        self.timer.start()

    def stop(self):
        self.timer.stop()
        self.pos = None
        self.time_period.particle_systems.remove(self)
        self.particles = []
        self.free_particles = []

    def setup_particle(self, particle):
        direction = self.random_direction()

        velocity = self.random_float(self.min_initial_speed,
                                     self.max_initial_speed)
        particle.velocity = (velocity * direction[0],
                             velocity * direction[1])

        acceleration = self.random_float(self.min_acceleration,
                                         self.max_acceleration)
        particle.acceleration = (acceleration * direction[0],
                                 acceleration * direction[1])

        particle.lifetime = self.random_float(self.min_lifetime,
                                              self.max_lifetime)
        particle.scale = self.random_float(self.min_scale,
                                           self.max_scale)
        particle.rotation_speed = \
            self.random_float(self.min_rotation_speed,
                              self.max_rotation_speed)
        particle.pos = self.pos
        particle.elapsed_time = 0.0
        particle.rotation = self.random_float(0.0, 360.0)

    def random_direction(self):
        angle = self.random_float(0, 2 * math.pi)
        return (math.cos(angle), math.sin(angle))

    def random_float(self, min_value, max_value):
        return min_value + random.random() * (max_value - min_value)

    def draw(self, surface):
        for particle in self.particles:
            if particle.active:
                particle.draw(surface)

    def on_particle_update(self):
        active_count = 0

        for particle in self.particles:
            if particle.active:
                active_count += 1
                particle.update(self.timer.ms / 1000.0)

                if not particle.active:
                    self.free_particles.append(particle)

        if not self.repeat and active_count == 0:
            self.stop()
        elif self.repeat:
            self.add_particles()


class ExplosionParticleSystem(ParticleSystem):
    def __init__(self, *args, **kwargs):
        super(ExplosionParticleSystem, self).__init__(max_particles=30,
                                                      *args, **kwargs)

        self.particle_filename = 'explosion'
        self.min_lifetime = 0.3
        self.max_lifetime = 0.5
        self.min_initial_speed = 200
        self.max_initial_speed = 300
        self.min_particles = 25
        self.min_scale = 0.3
        self.max_scale = 1.0
        self.min_rotation_speed = -360.0
        self.max_rotation_speed = 360.0

    def setup_particle(self, particle):
        super(ExplosionParticleSystem, self).setup_particle(particle)

        particle.acceleration = \
            (-particle.velocity[0] / particle.lifetime,
             -particle.velocity[1] / particle.lifetime)
