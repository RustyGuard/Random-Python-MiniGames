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
    def __init__(self, game):
        self.game = game
        self.childs: List[Cell] = []
        self.placed = False
        self.color = randcolor()

    def fall(self):
        for cell in self.childs:
            if cell.on_ground():
                self.placed = True
                for _ in range(3):
                    FallingParticle(cell.rect.centerx, cell.rect.bottom, randint(0, 180), uniform(-2, 2), uniform(1, 5), randint(0, 10), self.game.particles, color=self.color)
        if self.placed:
            for cell in self.childs:
                cell.static = True
        else:
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
        self.rect = Rect(0, 0, game.cell_size, game.cell_size)
        self.update_rect()
        game.grid[self.x, self.y] = self
        super().__init__(game.group)

    def on_ground(self):
        if self.y + 1 >= self.game.height:
            return True
        cell = self.game.grid.get((self.x, self.y + 1), None)
        if cell is not None and cell.static:
            return True
        return False

    def update_rect(self):
        self.rect.topleft = self.game.offset[0] + self.x * self.game.cell_size, self.game.offset[
            1] + self.y * self.game.cell_size

    def fall(self):
        self.y += 1
        self.game.grid[self.x, self.y] = self
        self.update_rect()


class Tetris:
    def __init__(self, offset, cell_size, width, height):
        self.group = Group()
        self.particles = Group()
        self.offset = offset
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Cell] = {}
        self.current_brick = Brick(self)
        self.current_brick.childs.append(Cell(0, 0, self.current_brick.color, self))
        self.fall_delay = 2
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
            2, 2, [
                (0, 0),
                (1, 0),
                (0, 1),
                (1, 1)
            ]
        ))

    def update(self, event):
        if event.type == TIMER_UPDATE:
            self.particles.update(event)
            if self.paused:
                return

            self.fall_time += 1
            if self.fall_time >= self.fall_delay:
                self.fall_time = 0
                # print('fall')
                self.current_brick.fall()
                if self.current_brick.placed:
                    for _ in range(50):
                        rand = randint(0, len(self.patterns) - 1)
                        pattern = self.patterns[rand]
                        x = randint(0, self.width - pattern[0])
                        for i, j in pattern[2]:
                            if self.grid.get((x + i, j), None) is not None:
                                break
                        else:
                            self.current_brick = Brick(self)
                            for i, j in pattern[2]:
                                self.current_brick.childs.append(Cell(x + i, j, self.current_brick.color, self))
                            break
                    else:
                        self.paused = True
                        print('Game over')

    def draw(self, screen):
        self.group.draw(screen)
        pygame.draw.rect(screen, Color('blue'),
                         (self.offset[0], self.offset[1], self.width * self.cell_size, self.height * self.cell_size), 1)
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
        #     self.offset[0] + i * self.cell_size, self.offset[1] + j * self.cell_size, self.cell_size, self.cell_size), 3)


def main():
    pygame.init()
    width, height = 500, 500
    screen = pygame.display.set_mode((width, height))

    running = True
    clock = pygame.time.Clock()
    game = Tetris((5, 5), 25, 15, 15)

    pygame.time.set_timer(TIMER_UPDATE, 1000 // 60)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
            game.update(event)

        screen.fill(pygame.Color('lightgray'))
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
