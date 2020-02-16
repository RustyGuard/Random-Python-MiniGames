import math
from random import randint, uniform
from typing import Dict, Tuple, List

import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.sprite import Sprite, Group
from pygame.surface import Surface

from constants import *
from particles import randcolor, FallingParticle


class Brick:
    def __init__(self, game, pattern, offset):
        self.game = game
        self.childs: List[Cell] = []
        self.placed = False
        self.color = randcolor()
        self.pattern = pattern
        self.x = offset[0]
        self.y = offset[1]

    def invert(self):
        new_pattern = (self.pattern[1], self.pattern[0], [
            (self.pattern[1] - j - 1, i) for i, j in self.pattern[2]
        ])

        for i, j in new_pattern[2]:
            if self.game.out_of_bounds(self.x + i, self.y + j):
                break
            cell = self.game.grid.get((self.x + i, self.y + j), None)
            if cell is not None and cell.static:
                break
        else:
            self.pattern = new_pattern
            for i in self.childs:
                self.game.grid.pop((i.x, i.y), None)
                i.kill()
            self.childs.clear()
            for i, j in self.pattern[2]:
                self.childs.append(Cell(self.x + i, self.y + j, self.color, self.game))

    def move(self, x, y):
        for cell in self.childs:
            if cell.cannot_move(x, y):
                for _ in range(3):
                    FallingParticle(cell.rect.centerx, cell.rect.bottom, randint(0, 180), uniform(-2, 2), uniform(1, 5),
                                    randint(0, 10), self.game.particles, color=self.color)
                break
        else:
            self.x += x
            self.y += y
            for cell in self.childs:
                self.game.grid.pop((cell.x, cell.y), None)
            for cell in self.childs:
                cell.move(x, y)

    def fall(self):
        for cell in self.childs:
            if cell.on_ground():
                self.placed = True
                for _ in range(3):
                    FallingParticle(cell.rect.centerx, cell.rect.bottom, randint(0, 180), uniform(-2, 2), uniform(1, 5),
                                    randint(0, 10), self.game.particles, color=self.color)
        if self.placed:
            for cell in self.childs:
                cell.static = True
        else:
            self.y += 1
            for cell in self.childs:
                self.game.grid.pop((cell.x, cell.y), None)
            for cell in self.childs:
                cell.fall()


class Cell(Sprite):
    def __init__(self, x, y, color, game):
        self.x = x
        self.y = y
        self.color = color
        self.game = game
        self.static = False
        self.image = Surface((game.cell_size, game.cell_size), pygame.SRCALPHA)
        self.image.fill(color)
        pygame.draw.rect(self.image, Color('gray'), (0, 0, game.cell_size, game.cell_size), 2)
        self.rect = Rect(game.offset[0], game.offset[1], game.cell_size, game.cell_size)
        game.grid[self.x, self.y] = self
        super().__init__(game.group)

    def on_ground(self):
        if self.y + 1 >= self.game.height:
            return True
        cell = self.game.grid.get((self.x, self.y + 1), None)
        if cell is not None and cell.static:
            return True
        return False

    def cannot_move(self, x, y):
        if self.x + x < 0 or self.x + x >= self.game.width:
            return True
        if self.y + y < 0 or self.y + y >= self.game.height:
            return True
        cell = self.game.grid.get((self.x + x, self.y + y), None)
        if cell is not None and cell.static:
            return True
        return False

    def get_rel_x(self):
        return self.x * self.game.cell_size + self.game.offset[0]

    def get_rel_y(self):
        return self.y * self.game.cell_size + self.game.offset[1]

    def update(self, event):
        if event.type == TIMER_UPDATE:
            dist_x = self.get_rel_x() - self.rect.left
            dist_y = self.get_rel_y() - self.rect.top
            if abs(dist_x) <= 5:
                self.rect.left += dist_x
            else:
                self.rect.left += math.ceil(dist_x / 4)

            if abs(dist_y) <= 5:
                self.rect.top += dist_y
            else:
                self.rect.top += math.ceil(dist_y / 4)

    def fall(self):
        self.y += 1
        self.game.grid[self.x, self.y] = self

    def move(self, x, y):
        self.x += x
        self.y += y
        self.game.grid[self.x, self.y] = self


class Tetris:
    def __init__(self, offset, cell_size, width, height):
        self.group = Group()
        self.particles = Group()
        self.offset = offset
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Cell] = {}
        self.fall_delay = 50
        self.bonus_speed = 1
        self.fall_time = 0
        self.patterns = []
        self.paused = False
        self.patterns.append((
            3, 1, [
                (0, 0),
                (1, 0),
                (2, 0)
            ]
        ))
        self.patterns.append((
            4, 1, [
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
            ]
        ))
        self.patterns.append((
            3, 2, [
                (0, 0),
                (1, 0),
                (2, 0),
                (1, 1)
            ]
        ))
        self.patterns.append((
            3, 2, [
                (0, 0),
                (1, 0),
                (2, 0),
                (2, 1)
            ]
        ))
        self.patterns.append((
            3, 2, [
                (0, 1),
                (1, 1),
                (2, 1),
                (2, 0)
            ]
        ))
        self.patterns.append((
            3, 2, [
                (0, 0),
                (1, 0),
                (1, 1),
                (2, 1)
            ]
        ))
        self.patterns.append((
            3, 2, [
                (0, 1),
                (1, 0),
                (1, 1),
                (2, 0)
            ]
        ))
        self.patterns.append((
            2, 2, [
                (0, 0),
                (1, 0),
                (0, 1),
                (1, 1)
            ]
        ))
        self.can_move = True
        self.current_brick = None
        self.generate_brick()

    def update(self, event):
        self.group.update(event)

        if event.type == TIMER_UPDATE:
            self.particles.update(event)
            if self.paused:
                return

            self.fall_time += self.bonus_speed
            if self.fall_time >= self.fall_delay:
                self.fall_time = 0
                self.can_move = True
                self.current_brick.fall()

                if pygame.key.get_pressed()[pygame.K_w]:
                    self.bonus_speed = max(1, self.bonus_speed - 100)

                if self.current_brick.placed:
                    self.generate_brick()
                    self.bonus_speed = 3

                for j in range(self.height):
                    for i in range(self.width):
                        cell = self.grid.get((i, j), None)
                        if cell is None or not cell.static:
                            break
                    else:
                        for i_ in range(self.width):
                            cell = self.grid.pop((i_, j), None)
                            cell.kill()
                        for j_ in range(j - 1, -1, -1):
                            for i_ in range(self.width):
                                cell = self.grid.pop((i_, j_), None)
                                if cell is not None:
                                    cell.move(0, 1)
        elif event.type == pygame.KEYDOWN:
            if self.can_move:
                if event.key == pygame.K_a:
                    self.current_brick.move(-1, 0)
                elif event.key == pygame.K_d:
                    self.current_brick.move(1, 0)
            if event.key == pygame.K_SPACE:
                self.current_brick.invert()
            if event.key == pygame.K_s:
                self.bonus_speed += 5

    def out_of_bounds(self, x, y):
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    def generate_brick(self):
        for _ in range(50):
            rand = randint(0, len(self.patterns) - 1)
            pattern = self.patterns[rand]
            x = randint(0, self.width - pattern[0])
            for i, j in pattern[2]:
                if self.grid.get((x + i, j), None) is not None:
                    break
            else:
                self.current_brick = Brick(self, pattern, (x, 0))
                for i, j in pattern[2]:
                    self.current_brick.childs.append(Cell(x + i, j, self.current_brick.color, self))
                break
        else:
            self.paused = True
            self.can_move = False
            for j in range(self.height):
                for i in range(self.width):
                    FallingParticle(i * self.cell_size, j * self.cell_size, randint(0, 180), uniform(-5, 5),
                                    uniform(-1, 5), randint(0, 3), self.particles, color=Color('red'))
            print('Game over')

    def draw(self, screen):
        self.group.draw(screen)
        pygame.draw.rect(screen, Color('blue'),
                         (self.offset[0], self.offset[1], self.width * self.cell_size, self.height * self.cell_size), 3)
        self.particles.draw(screen)
        # for i, j in self.grid:
        #     color = 'black'
        #     cell = self.grid.get((i, j), None)
        #     if cell is not None:
        #         if cell.static:
        #             color = 'red'
        #         else:
        #             color = 'blue'
        #     pygame.draw.rect(screen, Color(color), (
        #           self.offset[0] + i * self.cell_size,
        #           self.offset[1] + j * self.cell_size,
        #           self.cell_size, self.cell_size), 3)
        # pygame.draw.rect(screen, Color('yellow'), (
        #     self.offset[0] + self.current_brick.x * self.cell_size + randint(-2, 2),
        #     self.offset[1] + self.current_brick.y * self.cell_size + randint(-2, 2),
        #     self.cell_size, self.cell_size), 3)


def main():
    pygame.init()

    running = True
    clock = pygame.time.Clock()
    game = Tetris((5, 5), 25, 10, 20)
    width, height = game.width * game.cell_size + game.offset[0] * 2, game.height * game.cell_size + game.offset[1] * 2
    screen = pygame.display.set_mode((width, height))

    pygame.time.set_timer(TIMER_UPDATE, 1000 // 60)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
            game.update(event)

        screen.fill(pygame.Color('lightblue'))
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
