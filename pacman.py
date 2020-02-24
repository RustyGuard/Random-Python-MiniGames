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
        self.walls = {}
        with open('pacman_level.txt', mode='r') as level:
            for j, line in enumerate(level.readlines()):
                for i, sym in enumerate(line):
                    if self.is_outside(i, j):
                        continue
                    if sym == '#':
                        Wall(self, self.sprites, i, j)
                    else:
                        Coin(self, self.sprites, i, j)
        self.pacman = Pacman(self, 1, 1)
        self.sprites.add(self.pacman)
        self.sprites.add(Ghost(self, 3, 2))

    @property
    def get_background(self):
        return Color('lightgray')

    def draw(self, target):
        pygame.draw.rect(target, Color('darkblue'), (self.offset_x, self.offset_y, self.width * self.cell_size, self.height * self.cell_size), 1)
        super().draw(target)

    def is_empty(self, x, y):
        if self.is_outside(x, y):
            return False
        if (x, y) in self.walls:
            return False
        return True


class Wall(Sprite):
    def __init__(self, game, sprites, x, y):
        self.game: PacmanGame = game
        self.image = Surface((game.cell_size, game.cell_size))
        self.image.fill(Color('blue'))
        self.rect: Rect = self.image.get_rect()
        self.rect.topleft = game.offset_x + x * game.cell_size, game.offset_y + y * game.cell_size
        self.game.walls[x, y] = self

        super().__init__(sprites)


class Coin(Sprite):
    def __init__(self, game, sprites, x, y):
        self.game: PacmanGame = game
        self.image = Surface((game.cell_size / 2, game.cell_size / 2), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, Color('orange'), self.image.get_rect())
        self.rect: Rect = self.image.get_rect()
        self.rect.topleft = game.offset_x * 1.25 + x * game.cell_size, game.offset_y * 1.25 + y * game.cell_size
        self.game.walls[x, y] = self

        super().__init__(sprites)


class GameObject(Sprite):
    def __init__(self, game):
        self.game: PacmanGame = game
        super().__init__()

    def move(self, x, y):
        self.rect.x += x
        collided = pygame.sprite.spritecollide(self, self.game.sprites, False)
        for i in collided:
            if i != self and isinstance(i, Wall):
                if self.rect.x - i.rect.x < 0:
                    self.rect.right = i.rect.left
                else:
                    self.rect.left = i.rect.right
        self.rect.y += y
        collided = pygame.sprite.spritecollide(self, self.game.sprites, False)
        for i in collided:
            if i != self and isinstance(i, Wall):
                if i.rect.y - self.rect.y > 0:
                    self.rect.bottom = i.rect.top
                else:
                    self.rect.top = i.rect.bottom


class Pacman(GameObject):
    def __init__(self, game, x, y):
        self.image = Surface((game.cell_size, game.cell_size))
        self.image.fill(Color('yellow'))
        self.rect: Rect = self.image.get_rect()
        self.rect.topleft = game.offset_x + x * game.cell_size, game.offset_y + y * game.cell_size
        super().__init__(game)

    def move(self, x, y):
        super().move(x, y)
        for i in pygame.sprite.spritecollide(self, self.game.sprites, False):
            if i != self:
                if isinstance(i, Coin):
                    i.kill()

    def update(self, event):
        if event.type == TIMER_UPDATE:
            mx, my = 0, 0
            if pygame.key.get_pressed()[pygame.K_a]:
                mx -= 2
            if pygame.key.get_pressed()[pygame.K_d]:
                mx += 2
            if pygame.key.get_pressed()[pygame.K_w]:
                my -= 2
            if pygame.key.get_pressed()[pygame.K_s]:
                my += 2
            self.move(mx, my)


class Ghost(GameObject):
    def __init__(self, game, x, y):
        self.image = Surface((game.cell_size, game.cell_size))
        self.image.fill(Color('lightblue'))
        pygame.draw.rect(self.image, Color('black'), self.image.get_rect(), 1)
        self.rect: Rect = self.image.get_rect()
        self.rect.topleft = game.offset_x + x * game.cell_size, game.offset_y + y * game.cell_size
        super().__init__(game)

    def move(self, x, y):
        super().move(x, y)

    def update(self, event):
        if event.type == TIMER_UPDATE:
            mx, my = 0, 0
            dist_x = self.rect.centerx - self.game.pacman.rect.centerx
            dist_y = self.rect.centery - self.game.pacman.rect.centery
            if dist_x < 0:
                mx += 1
            elif dist_x > 0:
                mx -= 1
            if dist_y < 0:
                my += 1
            elif dist_y > 0:
                my -= 1
            self.move(mx, my)


if __name__ == '__main__':
    start_game(PacmanGame(25, 25, 25, 27, 27))
