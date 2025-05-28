from entity_component_system import EntityComponentSystem
from ecs_types import EntityId
from dataclasses import dataclass, field
from components import *
from systems import *
import math
import settings
import pygame
from pygame import Color
from pygame.time import Clock


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

        self.ecs.init_component(ColliderComponent)
        self.ecs.init_component(VelocityComponent)
        self.ecs.init_component(DamageOnContactComponent)
        self.ecs.init_component(HealthComponent)

        self.ecs.init_system(velocity_system)
        self.ecs.init_system(damage_on_contact_system)
        self.ecs.init_system(death_system)

        self.ecs.create_entity(self.create_arrow(
            x=0, y=0, angle=45, speed=2, damage=50))
        self.ecs.create_entity(self.create_arrow(
            x=500, y=0, angle=135, speed=1.5, damage=50))
        self.ecs.create_entity(self.create_arrow(
            x=0, y=500, angle=-45, speed=1.1, damage=50))
        self.ecs.create_entity(self.create_arrow(
            x=500, y=500, angle=-135, speed=1, damage=50))
        self.ecs.create_entity(self.create_dummy(x=250, y=250, health=200))

    def create_arrow(self, x: float, y: float, angle: int, speed: float, damage: int):
        arrow_radius = 15
        return [
            ColliderComponent(x, y, arrow_radius),
            VelocityComponent(
                speed_x=math.cos(math.radians(angle)) * speed,
                speed_y=math.sin(math.radians(angle)) * speed
            ),
            DamageOnContactComponent(damage)
        ]

    def create_dummy(self, x: float, y: float, health: int):
        dummy_radius = 50
        return [
            ColliderComponent(x, y, dummy_radius),
            HealthComponent(
                max_amount=health,
            )
        ]

    def run(self):
        while self.running:
            self.display.fill((93, 161, 48))
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

            self.ecs.update()

            for entity_id, (collider,) in self.ecs.get_entities_with_components(ColliderComponent):
                pygame.draw.circle(self.display, Color('gray'),
                                   (collider.x, collider.y), collider.radius)

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
