import pygame
import sys
from settings import Screen
from Entities import Player


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('MyGame')
        self._screen = pygame.display.set_mode((Screen.WIDTH, Screen.HEIGHT))
        self.display = pygame.Surface((self._screen.get_width(
        )//Screen.DISPLAY_RATIO, self._screen.get_height()//Screen.DISPLAY_RATIO))
        self.clock = pygame.time.Clock()
        self.player = Player(
            (self.display.get_width()//2, self.display.get_height()//2), 'Player/idle00.png')

    def run(self):
        while True:
            self.display.fill(Screen.BACKGROUND_COLOR)

            self.player.update()
            self.player.render(self.display)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._screen.blit(pygame.transform.scale(
                self.display, self._screen.get_size()))
            pygame.display.update()
            self.clock.tick(60)


Game().run()
