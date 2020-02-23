import pygame
from pygame import Color
from pygame.font import Font
from pygame.sprite import Group

from constants import TIMER_UPDATE, TIMER_SECOND


class Game:
    def __init__(self, offset_x, offset_y, cell_size, width, height):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.cell_size = cell_size
        self.width = width
        self.height = height
        pygame.font.init()
        self.font = pygame.font.Font('fonts/Samson.ttf', cell_size)
        self.particles = Group()
        self.sprites = Group()
        self.gameover = False
        self.paused = False

    def is_outside(self, x, y):
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    def update(self, event):
        if not (self.gameover or self.paused):
            self.sprites.update(event)
        self.particles.update(event)

    def draw(self, target):
        self.sprites.draw(target)
        self.particles.draw(target)

    def get_size(self):
        return self.offset_x * 2 + self.width * self.cell_size, self.offset_y * 2 + self.height * self.cell_size

    @property
    def get_background(self):
        return Color('white')


def start_game(game: Game):
    pygame.init()
    size = game.get_size()
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    pygame.time.set_timer(TIMER_UPDATE, 1000 // 60)
    pygame.time.set_timer(TIMER_SECOND, 1000)

    running = True
    current_fps = 60
    frames = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.update(event)

        screen.fill(game.get_background)
        game.draw(screen)

        screen.blit(game.font.render(f'FPS: {current_fps}', True, Color('white')), (15, 5))

        pygame.display.flip()
        clock.tick(60)
        frames += 1
    pygame.quit()
