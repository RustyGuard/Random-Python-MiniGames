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
        self.pacman = Pacman(self, 25, 25)
        self.sprites.add(self.pacman)
        self.sprites.add(Ghost(self, 12, 12))

    @property
    def get_background(self):
        return Color('lightgray')

    def draw(self, target):
        pygame.draw.rect(target, Color('darkblue'), (self.offset_x, self.offset_y, self.width * self.cell_size, self.height * self.cell_size), 1)
        super().draw(target)

        # rel = self.pacman.get_grid_pos()
        # pygame.draw.rect(target, Color('red'), (self.offset_x + rel[0] * self.cell_size, self.offset_y + rel[1] * self.cell_size, self.cell_size, self.cell_size), 3)
        for i in self.sprites:
            if isinstance(i, Ghost):
                for node in i.nodes:
                    pygame.draw.rect(target, Color('green'), (self.offset_x + node.x * self.cell_size, self.offset_y + node.y * self.cell_size, self.cell_size, self.cell_size), 2)

    def is_empty(self, x, y):
        if self.is_outside(x, y):
            return False
        if (x, y) in self.walls:
            return False
        return True

    def get_neightbors(self, x, y):
        for i, j in [[0, -1], [1, 0], [0, 1], [-1, 0]]:
            if self.is_empty(x + i, y + j):
                yield x + i, y + j


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

        super().__init__(sprites)


class GameObject(Sprite):
    def __init__(self, game):
        self.game: PacmanGame = game
        super().__init__()

    def get_grid_pos(self):
        return (self.rect.centerx - self.game.offset_x) // self.game.cell_size, (self.rect.centery - self.game.offset_y) // self.game.cell_size

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
        self.image = Surface((game.cell_size - 2, game.cell_size - 2))
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
        self.nodes = []
        self.last_pacman = [-1, -1]
        self.current_node = None
        super().__init__(game)

    def move(self, x, y):
        super().move(x, y)

    def find_path(self):
        self.nodes.clear()
        node = find_path(self.game, *self.get_grid_pos(), *self.game.pacman.get_grid_pos())
        if node is None:
            return
        pac_pose = self.game.pacman.get_grid_pos()
        self.last_pacman[0] = pac_pose[0]
        self.last_pacman[1] = pac_pose[1]
        while node is not None:
            self.nodes.append(node)
            node = node.parent
        if self.nodes:
            self.nodes.pop()

    def update(self, event):
        if event.type == TIMER_UPDATE:
            pac_pose = self.game.pacman.get_grid_pos()
            if pac_pose[0] != self.last_pacman[0] or pac_pose[1] != self.last_pacman[1]:
                print('Pacman moved!', self.last_pacman, pac_pose)
                self.find_path()

            if self.current_node is None:
                if self.nodes:
                    self.current_node = self.nodes.pop()
                else:
                    self.find_path()
            else:
                mx, my = 0, 0
                dist_x = self.rect.x - (self.current_node.x * self.game.cell_size + self.game.offset_x)
                dist_y = self.rect.y - (self.current_node.y * self.game.cell_size + self.game.offset_y)

                if dist_x < 0:
                    mx += 1
                elif dist_x > 0:
                    mx -= 1
                if dist_y < 0:
                    my += 1
                elif dist_y > 0:
                    my -= 1
                if dist_x == 0 and dist_y == 0:
                    if self.nodes:
                        self.current_node = self.nodes.pop()
                    else:
                        self.find_path()
                else:
                    self.move(mx, my)


if __name__ == '__main__':

    start_game(PacmanGame(25, 25, 25, 27, 27))
