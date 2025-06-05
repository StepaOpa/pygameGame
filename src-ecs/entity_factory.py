# entity_factory.py
from components import *
from entity_component_system import EntityComponentSystem
from assets import AssetManager
import pygame
import math
from ecs_types import EntityId
from map_generator import generate_tile_entities_from_template
import settings


class EntityFactory:
    def __init__(self, ecs: EntityComponentSystem, assets: AssetManager, display: pygame.Surface):
        self.ecs = ecs
        self.assets = assets
        self.display = display

    def create_map(self) -> None:
        generate_tile_entities_from_template(settings.TileMap.TEMPLATE_PATH, self)

    def create_player(self, x, y) -> EntityId:
        position = pygame.Vector2(x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)
        sprite = self.assets.get_sprite('Player/idle00.png')
        return self.ecs.create_entity(
            [
                Position(position=position),
                GridPosition(x=x, y=y),
                Velocity(),
                Health(max_amount=100),
                Render(
                    sprite=sprite,
                    scale=1.0,
                    layer=1
                ),
                PlayerTag(),
                Collider(position=position)
            ]
        )

    def create_tile(self, x: int, y: int, tile_type: str, variant: str, walkable: bool) -> EntityId:
        
        if tile_type == 'floor':
            sprite = self.assets.get_sprite(variant)
        else:
            sprite = self.assets.get_tile_sprite(variant)

        position = pygame.Vector2(x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)

        return self.ecs.create_entity(
            [
                Position(position=position),
                GridPosition(x=x, y=y),
                Render(sprite=sprite, scale=settings.TileMap.TILE_SIZE/16, layer=0),
                TileComponent(tile_type=tile_type, variant=variant, walkable=walkable)
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
                Position(position=position),
                Collider(position=position, radius=arrow_radius),
                Velocity(velocity=velocity),
                DamageOnContact(damage),
                Render(),
                RenderTarget(surface=self.display, assets=self.assets)
            ]
        )

    def create_dummy(self, x: float = 250, y: float = 250, health: int = 200) -> EntityId:
        dummy_radius = 50
        position = pygame.Vector2(x, y)
        return self.ecs.create_entity(
            [
                Position(position=position),
                Collider(position=position, radius=dummy_radius),
                Health(max_amount=health),
                Render(),
                RenderTarget(surface=self.display, assets=self.assets)
            ]
        )
