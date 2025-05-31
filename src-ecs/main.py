from entity_component_system import EntityComponentSystem
from ecs_types import EntityId
from components import *
from systems import *
from assets import AssetManager
import math
import settings
import pygame
from pygame import Color
from entity_factory import EntityFactory


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('MyGame')
        self._screen = pygame.display.set_mode(
            (settings.ScreenSettngs.WIDTH, settings.ScreenSettngs.HEIGHT))
        self.display = pygame.Surface((self._screen.get_width(
        )//settings.ScreenSettngs.DISPLAY_RATIO, self._screen.get_height()//settings.ScreenSettngs.DISPLAY_RATIO))

        self.clock = pygame.time.Clock()
        self.running = True

        self.ecs = EntityComponentSystem()
        self.assets = AssetManager()
        self.factory = EntityFactory(self.ecs, self.assets, self.display)

        # init components
        self.ecs.init_component(PositionComponent)
        self.ecs.init_component(ColliderComponent)
        self.ecs.init_component(VelocityComponent)
        self.ecs.init_component(DamageOnContactComponent)
        self.ecs.init_component(HealthComponent)
        self.ecs.init_component(TilemapComponent)
        self.ecs.init_component(RenderTargetComponent)
        self.ecs.init_component(RenderComponent)
        self.ecs.init_component(PlayerTag)
        # init systems

        self.ecs.init_system(input_system)
        self.ecs.init_system(velocity_system)
        self.ecs.init_system(damage_on_contact_system)
        self.ecs.init_system(death_system)
        self.ecs.init_system(tilemap_cache_system)
        self.ecs.init_system(tilemap_system)
        self.ecs.init_system(render_system)

        # map
        self.factory.create_map()
        # player
        self.factory.create_player(100,100)

    def run(self):
        while self.running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

            self.display.fill(Color('black'))
            self.ecs.update()
            self._screen.blit(pygame.transform.scale(
                self.display, self._screen.get_size()), (0, 0))
            pygame.display.flip()

            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
