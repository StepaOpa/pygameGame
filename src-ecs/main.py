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
        self.ecs.init_component(Position)
        self.ecs.init_component(GridPosition)
        self.ecs.init_component(TileComponent)
        self.ecs.init_component(Collider)
        self.ecs.init_component(Velocity)
        self.ecs.init_component(DamageOnContact)
        self.ecs.init_component(Health)
        self.ecs.init_component(RenderTarget)
        self.ecs.init_component(Render)
        self.ecs.init_component(PlayerTag)
        self.ecs.init_component(EnemyTag)
        self.ecs.init_component(TurnComponent)

        # add variables
        self.ecs.add_variable('render_target', RenderTarget(surface=self.display, assets=self.assets))
        
        # init systems
        self.ecs.add_system(InputSystem())
        self.ecs.add_system(GridMovementSystem())
        self.ecs.add_system(PositionSyncSystem())
        self.ecs.add_system(DamageOnContactSystem())
        self.ecs.add_system(DeathSystem())
        self.ecs.add_system(RenderSystem())
        self.enemy_pathfinding_system = EnemyPathfindingSystem()
        self.ecs.add_system(self.enemy_pathfinding_system)

        # map
        self.factory.create_map()
        # player
        self.factory.create_player(2, 2)
        # enemy
        self.factory.create_enemy()
        self.factory.create_enemy()
        
        # Создаем сущность для управления ходами
        self.ecs.create_entity([TurnComponent()])

    def run(self):
        render_system: RenderSystem = self.ecs.get_system(RenderSystem)
        
        while self.running:
            events = pygame.event.get()
            self.ecs.add_variable('events', events)

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.display.fill(Color('black'))
            self.ecs.update()
            render_system.draw_all(self.ecs)
            self.enemy_pathfinding_system.draw_debug(self.ecs)
            
            self._screen.blit(pygame.transform.scale(
                self.display, self._screen.get_size()), (0, 0))
            pygame.display.flip()

            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
