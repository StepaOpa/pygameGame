import pygame
import sys
from settings import Screen
from entities import Player, Enemy


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

        self.enemies = [Enemy((self.display.get_width()//4 + i*50, self.display.get_height()//4),
                              'Enemies/Vampire/vampire_idle.png', self.player) for i in range(10)]

    def run(self):
        while True:
            # display
            self.display.fill(Screen.BACKGROUND_COLOR)

            # player
            self.player.update()
            self.player.render(self.display)

            for enemy in self.enemies:
                enemy.update()
                enemy.render(self.display)

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._screen.blit(pygame.transform.scale(
                self.display, self._screen.get_size()))
            pygame.display.update()
            self.clock.tick(60)


Game().run()
