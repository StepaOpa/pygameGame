import pygame
import sys
import settings
from entities import Player, Enemy
from map import Tilemap
import utils
import assets


class Game:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('MyGame')
        self._screen = pygame.display.set_mode(
            (settings.ScreenSettngs.WIDTH, settings.ScreenSettngs.HEIGHT))
        self.display = pygame.Surface((self._screen.get_width(
        )//settings.ScreenSettngs.DISPLAY_RATIO, self._screen.get_height()//settings.ScreenSettngs.DISPLAY_RATIO))
        self.clock = pygame.time.Clock()
        self.player = Player(
            (self.display.get_width()//2, self.display.get_height()//2), 'Player/idle00.png')

        self.enemies = [Enemy((self.display.get_width()//4 + i*50, self.display.get_height()//4),
                              'Enemies/Vampire/vampire_idle.png', self.player) for i in range(10)]

        self.physics_entities = self.enemies + [self.player]
        self.assets_manager = assets.AssetManager()
        self.tilemap = Tilemap(self.assets_manager)

    def run(self):
        while True:
            # display
            self.display.fill(settings.ScreenSettngs.BACKGROUND_COLOR)

            # map
            self.tilemap.render(self.display)

            # delta_time
            delta_time = self.clock.tick(
                settings.GameSettings.TARGET_FPS) / 1000.0 * settings.GameSettings.TARGET_FPS

            # player
            self.player.update(delta_time, self.physics_entities)
            self.player.render(self.display)

            # enemies
            for enemy in self.enemies:
                enemy.update(delta_time, self.physics_entities)
                enemy.render(self.display)

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._screen.blit(pygame.transform.scale(
                self.display, self._screen.get_size()))
            pygame.display.update()
            self.clock.tick(settings.GameSettings.TARGET_FPS)


Game().run()
