import random
from random import randint, uniform, sample, choice

import pygame
from pygame import Color
from pygame.rect import Rect

from game import Game, start_game
from particles import FallingParticle


class Minesweeper(Game):
    def __init__(self, offset_x, offset_y, cell_size, width, height, mine_count):
        super().__init__(offset_x, offset_y, cell_size, width, height)
        self.win = False
        self.width = width
        self.height = height
        self.board = [[0] * height for _ in range(width)]
        # значения по умолчанию
        self.colors = {1: "lightblue", 2: "green", 3: 'red', 4: 'blue'}
        self.board = [[-1] * height for _ in range(width)]
        i = 0
        while i < mine_count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.board[x][y] == -1:
                self.board[x][y] = 10
                i += 1

    def get_cell(self, mouse_pos):
        x, y = mouse_pos[0] - self.offset_x, mouse_pos[1] - self.offset_y
        if not (0 < x < self.width * self.cell_size and
                0 < y < self.height * self.cell_size):
            return None
        return x // self.cell_size, y // self.cell_size

    def get_click(self, mouse_pos, button):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell, button)

    def get_neightbours(self, x, y):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if self.is_outside(x + dx, y + dy):
                    continue
                yield self.board[x + dx][y + dy]

    def mark_cell(self, cell):
        x, y = cell
        val = self.board[x][y]
        if val == 10:
            self.board[x][y] = 12
        elif val == -1:
            self.board[x][y] = 13
        elif val == 12:
            self.board[x][y] = 10
        elif val == 13:
            self.board[x][y] = -1
        self.check()

    def open_cell(self, cell):
        x, y = cell
        val = self.board[x][y]

        if val == 10:
            self.board[x][y] = 11
            self.gameover = True
            for _ in range(20):
                FallingParticle((x + 0.5) * self.cell_size, (y + 0.5) * self.cell_size, randint(0, 180), uniform(-5, 5),
                                uniform(-1, -15), randint(0, 3), self.particles,
                                color=Color(choice(['orange', 'red', 'gray'])))
            return

        if val != -1:
            return

        s = 0
        for i in self.get_neightbours(x, y):
            if i in [10, 11, 12]:
                s += 1
        self.board[x][y] = s

        if s == 0:
            cells = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
            for i in cells:
                if self.is_outside(x + i[0], y + i[1]):
                    continue
                self.open_cell((x + i[0], y + i[1]))

    def on_click(self, cell, button):
        if not (self.gameover or self.win):
            if button == 1:
                self.open_cell(cell)
            elif button == 3:
                self.mark_cell(cell)

    def check(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[x][y] in [10, 13]:
                    return False
        self.win = True
        for _ in range(20):
            FallingParticle(100 + randint(-50, 50), 50, randint(0, 180), uniform(-5, 5),
                            uniform(-1, -10), randint(0, 3), self.particles)
        return True

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.get_click(event.pos, event.button)
        super().update(event)

    @property
    def get_background(self):
        return Color('gray')

    def get_cell_rect(self, x, y):
        return Rect(x * self.cell_size + self.offset_x, y * self.cell_size + self.offset_y,
                    self.cell_size, self.cell_size)

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                val = self.board[x][y]
                rect = self.get_cell_rect(x, y)

                if 9 > val >= 0:
                    pygame.draw.rect(screen, pygame.Color('lightgray'), rect)
                elif val == 11:
                    pygame.draw.rect(screen, pygame.Color('red'), rect)
                elif val in [12, 13]:
                    pygame.draw.rect(screen, pygame.Color('orange'), rect)

                if 9 > self.board[x][y] > 0:
                    text = self.font.render(str(self.board[x][y]), 1, Color(self.colors.get(self.board[x][y], 'red')))
                    screen.blit(text, rect.move(7, 0))

                pygame.draw.rect(screen, pygame.Color('darkgray'), rect, 1)
        super().draw(screen)
        if self.gameover:
            screen.blit(self.font.render('Game over', True, Color('red')), (100, 5))
        if self.win:
            screen.blit(self.font.render('You win', True, Color('green')), (100, 5))


if __name__ == '__main__':
    start_game(Minesweeper(15, 30, 25, 10, 20, 1))
