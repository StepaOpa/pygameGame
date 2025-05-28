# game.py
import pygame
import sys
import settings
from map import Tilemap
import assets
from ecs import ECS
from components import *
from systems import *


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('MyGame')
        self._screen = pygame.display.set_mode(
            (settings.ScreenSettngs.WIDTH, settings.ScreenSettngs.HEIGHT))
        self.display = pygame.Surface((self._screen.get_width(
        )//settings.ScreenSettngs.DISPLAY_RATIO, self._screen.get_height()//settings.ScreenSettngs.DISPLAY_RATIO))

        self.clock = pygame.time.Clock()

        # ECS init
        self.ecs = ECS()
        self.init_entities()
        self.init_systems()

        self.running = True

    def init_entities(self):
        player = self.ecs.create_entity()

        self.ecs.add_component(player, Transform(x=100, y=100))
        self.ecs.add_component(player, Physics())
        self.ecs.add_component(player, PlayerController())

        player_image = pygame.Surface((32, 32))
        player_image.fill((255, 0, 0))
        self.ecs.add_component(player, Sprite(image=player_image))

    def init_systems(self):
        self.ecs.add_system(InputSystem(self.ecs))
        self.ecs.add_system(PhysicsSystem(self.ecs))
        self.ecs.add_system(RenderSystem(self.ecs))

    def run(self):
        while True:
            # clear screen
            self.display.fill(settings.ScreenSettngs.BACKGROUND_COLOR)

            # delta_time
            delta_time = self.clock.tick(60) / 1000.0

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # update
            self.ecs.update(delta_time)

            # render display
            self._screen.blit(pygame.transform.scale(
                self.display, self._screen.get_size()))
            pygame.display.update()
            self.clock.tick(settings.GameSettings.TARGET_FPS)


if __name__ == "__main__":
    Game().run()
