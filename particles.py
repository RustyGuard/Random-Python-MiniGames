import math
import random
from random import uniform, randint

import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface


def randcolor():
    return randint(0, 255), randint(0, 255), randint(0, 255)


class Particle(Sprite):
    gravity = (0.0, 0.2)

    def __init__(self, x, y, z, speed_x, speed_y, speed_z, particles, color=None):
        self.x = x
        self.y = y
        self.z = z
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed_z = speed_z

        self.default_image = Surface((10, 10), pygame.SRCALPHA)
        self.default_image.fill(color if color else randcolor())

        angle = (180 / math.pi) * self.z
        self.image = pygame.transform.rotate(self.default_image, int(angle))

        self.rect = Rect(0, 0, 15, 15)
        self.rect.center = x, y
        self.particles = particles

        super().__init__(particles)

    def move(self, x, y):
        self.x += x
        self.y += y
        self.rect.center = self.x, self.y

    def update_image(self):
        angle = (180 / math.pi) * self.z
        self.image = pygame.transform.rotate(self.default_image, int(angle))

    def update(self, *args):
        self.move(self.speed_x, self.speed_y)
        self.speed_x += Particle.gravity[0]
        self.speed_y += Particle.gravity[1]
        self.z += self.speed_z
        self.update_image()
        if self.y > 500:
            self.kill()


class PopParticle(Particle):
    mult = 0.9

    def can_pop(self):
        return abs(self.speed_x) > 0.01 or abs(self.speed_y) > 0.01

    def update(self, *args):
        super().update(*args)
        if self.y > 500:
            self.kill()
            if self.can_pop():
                PopParticle(self.x, self.y, self.z, self.speed_x * PopParticle.mult,
                            -abs(self.speed_y) * PopParticle.mult, -self.speed_z,
                            self.particles)
        elif self.y < 0:
            self.kill()
            if self.can_pop():
                PopParticle(self.x, self.y, self.z, self.speed_x * PopParticle.mult,
                            abs(self.speed_y) * PopParticle.mult, -self.speed_z,
                            self.particles)
        elif self.x > 500:
            self.kill()
            if self.can_pop():
                PopParticle(self.x, self.y, self.z, -abs(self.speed_x) * PopParticle.mult,
                            self.speed_y * PopParticle.mult, -self.speed_z,
                            self.particles)
        elif self.x < 0:
            self.kill()
            if self.can_pop():
                PopParticle(self.x, self.y, self.z, abs(self.speed_x) * PopParticle.mult,
                            self.speed_y * PopParticle.mult, -self.speed_z,
                            self.particles)


class FallingParticle(Particle):
    def update(self, *args):
        super().update(*args)
        if self.y > 550:
            self.kill()


def test():
    pygame.init()
    width, height = 500, 500
    screen = pygame.display.set_mode((width, height))

    running = True
    clock = pygame.time.Clock()
    particles = pygame.sprite.Group()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    FallingParticle(*event.pos, randint(0, 359),
                                    uniform(-1.0, 1.0) * 4, randint(-10, -5), uniform(-0.1, 0.1),
                                    particles)
                elif event.button == 5:
                    PopParticle(*event.pos, randint(0, 359),
                                uniform(-1.0, 1.0) * 4, randint(-10, -5), uniform(-0.1, 0.1),
                                particles)

        screen.fill(pygame.Color('white'))
        particles.draw(screen)
        particles.update()
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    test()
