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

        # add variables
        self.ecs.add_variable('render_target', RenderTarget(surface=self.display, assets=self.assets))
        
        # init systems
        self.ecs.add_system(InputSystem())
        self.ecs.add_system(GridMovementSystem())
        self.ecs.add_system(PositionSyncSystem())
        self.ecs.add_system(DamageOnContactSystem())
        self.ecs.add_system(DeathSystem())
        self.ecs.add_system(RenderSystem())

        # map
        self.factory.create_map()
        # player
        self.factory.create_player(2, 2)

    def run(self):
        render_system: RenderSystem = self.ecs.get_system(RenderSystem)
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    self.handle_input(event.key)


            self.display.fill(Color('black'))
            self.ecs.update()
            render_system.draw_all(self.ecs)
            
            self._screen.blit(pygame.transform.scale(
                self.display, self._screen.get_size()), (0, 0))
            pygame.display.flip()

            self.clock.tick(60)

    def handle_input(self, key):
        player_entities = list(self.ecs.get_entities_with_components(PlayerTag, GridPosition))
        if not player_entities:
            return
            
        player_id, (player_tag, grid_pos) = player_entities[0]
        
        movement_system: GridMovementSystem = self.ecs.get_system(GridMovementSystem)

        dx, dy = 0, 0
        if key == pygame.K_LEFT or key == pygame.K_a: dx = -1
        if key == pygame.K_RIGHT or key == pygame.K_d: dx = 1
        if key == pygame.K_UP or key == pygame.K_w: dy = -1
        if key == pygame.K_DOWN or key == pygame.K_s: dy = 1

        if dx != 0 or dy != 0:
            new_x, new_y = grid_pos.x + dx, grid_pos.y + dy
            if movement_system.is_walkable(new_x, new_y, self.ecs):
                grid_pos.x = new_x
                grid_pos.y = new_y


if __name__ == "__main__":
    Game().run()
