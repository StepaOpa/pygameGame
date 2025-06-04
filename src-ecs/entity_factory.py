# entity_factory.py
from components import *
from entity_component_system import EntityComponentSystem
from assets import AssetManager
import pygame
import math
from ecs_types import EntityId


class EntityFactory:
    def __init__(self, ecs: EntityComponentSystem, assets: AssetManager, display: pygame.Surface):
        self.ecs = ecs
        self.assets = assets
        self.display = display

    def create_map(self) -> EntityId:
        return self.ecs.create_entity(
            [TilemapComponent(), RenderTargetComponent(surface=self.display, assets=self.assets)]
        )

    def create_player(self, x, y) -> EntityId:
        position = pygame.Vector2(x, y)
        sprite = self.assets.get_sprite('Player/idle00.png')
        return self.ecs.create_entity(
            [
                PositionComponent(position=position),
                VelocityComponent(),
                HealthComponent(max_amount=100),
                RenderComponent(
                    sprite=sprite,
                    scale=1.0
                ),
                RenderTargetComponent(surface=self.display, assets=self.assets),
                PlayerTag(),
                ColliderComponent(position=position)
            ]
        )

    def create_arrow(self, x: float, y: float, angle: int, speed: float, damage: int) -> EntityId:
        arrow_radius = 15
        position = pygame.Vector2(x, y)
        velocity = pygame.Vector2(
            math.cos(math.radians(angle)) * speed,
            math.sin(math.radians(angle)) * speed
        )
        return self.ecs.create_entity(
            [
                PositionComponent(position=position),
                ColliderComponent(position=position, radius=arrow_radius),
                VelocityComponent(velocity=velocity),
                DamageOnContactComponent(damage),
                RenderComponent(),
                RenderTargetComponent(surface=self.display, assets=self.assets)
            ]
        )

    def create_dummy(self, x: float = 250, y: float = 250, health: int = 200) -> EntityId:
        dummy_radius = 50
        position = pygame.Vector2(x, y)
        return self.ecs.create_entity(
            [
                PositionComponent(position=position),
                ColliderComponent(position=position, radius=dummy_radius),
                HealthComponent(max_amount=health),
                RenderComponent(),
                RenderTargetComponent(surface=self.display, assets=self.assets)
            ]
        )
