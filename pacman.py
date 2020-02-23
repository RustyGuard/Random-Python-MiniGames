import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.sprite import Group, Sprite
from pygame.surface import Surface

from a_star import *
from constants import TIMER_UPDATE
from game import start_game, Game


class PacmanGame(Game):
    def __init__(self, offset_x, offset_y, cell_size, width, height):
        super().__init__(offset_x, offset_y, cell_size, width, height)
        self.sprites.add(Pacman(self, 1, 1))
        self.walls = {}
        with open('pacman_level.txt', mode='r') as level:
            for j, line in enumerate(level.readlines()):
                for i, sym in enumerate(line):
                    if sym == '#':
                        Wall(self, self.sprites, i, j)

    @property
    def get_background(self):
        return Color('lightgray')

    def draw(self, target):
        pygame.draw.rect(target, Color('darkblue'), (self.offset_x, self.offset_y, self.width * self.cell_size, self.height * self.cell_size), 1)
        super().draw(target)


class Wall(Sprite):
    def __init__(self, game, sprites, x, y):
        self.game: PacmanGame = game
        self.image = Surface((game.cell_size, game.cell_size))
        self.image.fill(Color('blue'))
        self.rect: Rect = self.image.get_rect()
        self.rect.topleft = game.offset_x + x * game.cell_size, game.offset_y + y * game.cell_size
        self.game.walls[x, y] = self

        super().__init__(sprites)


class Pacman(Sprite):
    def __init__(self, game, x, y):
        self.game: PacmanGame = game
        self.image = Surface((game.cell_size, game.cell_size))
        self.image.fill(Color('yellow'))
        self.rect: Rect = self.image.get_rect()
        self.rect.topleft = game.offset_x + x * game.cell_size, game.offset_y + y * game.cell_size
        super().__init__()

    def move(self, x, y):
        self.rect.x += x
        collided = pygame.sprite.spritecollide(self, self.game.sprites, False)
        for i in collided:
            if i != self:
                if self.rect.x - i.rect.x < 0:
                    self.rect.right = i.rect.left
                else:
                    self.rect.left = i.rect.right
        self.rect.y += y
        collided = pygame.sprite.spritecollide(self, self.game.sprites, False)
        for i in collided:
            if i != self:
                if i.rect.y - self.rect.y > 0:
                    self.rect.bottom = i.rect.top
                else:
                    self.rect.top = i.rect.bottom

    def update(self, event):
        if event.type == TIMER_UPDATE:
            mx, my = 0, 0
            if pygame.key.get_pressed()[pygame.K_a]:
                mx -= 1
            if pygame.key.get_pressed()[pygame.K_d]:
                mx += 1
            if pygame.key.get_pressed()[pygame.K_w]:
                my -= 1
            if pygame.key.get_pressed()[pygame.K_s]:
                my += 1
            self.move(mx, my)


if __name__ == '__main__':
    start_game(PacmanGame(25, 25, 25, 27, 27))
