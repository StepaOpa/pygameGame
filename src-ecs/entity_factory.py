# entity_factory.py
from components import *
from entity_component_system import EntityComponentSystem
from assets import AssetManager
import pygame
import math
from ecs_types import EntityId
from map_generator import generate_tile_entities_from_template
import settings
import random


class EntityFactory:
    def __init__(self, ecs: EntityComponentSystem, assets: AssetManager, display: pygame.Surface):
        self.ecs = ecs
        self.assets = assets
        self.display = display

    def create_map(self) -> None:
        generate_tile_entities_from_template(settings.TileMap.TEMPLATE_PATH, self)

    def create_player(self, x, y) -> EntityId:
        position = pygame.Vector2(x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)
        # Загружаем кадры анимации простоя игрока
        frames = []
        for i in range(4):
            path = f'Player/idle/idle_{i}.png'
            frames.append(self.assets.get_sprite(path))
        if not frames:
            frames.append(self.assets.get_sprite('Player/idle_0.png'))
        sprite = frames[0]
        return self.ecs.create_entity(
            [
                Position(position=position),
                GridPosition(x=x, y=y),
                Velocity(),
                Health(max_amount=100),
                Attack(damage=10),
                Inventory(),
                Animation(frames=frames, frame_time=200),
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
    
    def _get_walkable_tiles(self) -> List:
        walkable_tiles = []
        for entity_id, (grid_pos, tile) in self.ecs.get_entities_with_components(GridPosition, TileComponent):
            if tile.walkable:
                walkable_tiles.append((grid_pos.x, grid_pos.y))
        return walkable_tiles
        
    
    def create_enemy(self) -> EntityId:
        # Получаем все проходимые клетки
        walkable_tiles = self._get_walkable_tiles()
        if not walkable_tiles:
            return None
        
        # Выбираем случайную проходимую клетку
        x, y = random.choice(walkable_tiles)
        position = pygame.Vector2(x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)
        
        # Загружаем кадры анимации врага (пример: vampire_idle.png, vampire_idle2.png...)
        frames = []
        for i in range(3):
            path = f'Enemies/Vampire/vampire_idle_{i}.png'
            frames.append(self.assets.get_sprite(path))
        if not frames:
            frames.append(self.assets.get_sprite('Enemies/Vampire/vampire_idle.png'))
        sprite = frames[0]
        
        return self.ecs.create_entity(
            [
                Position(position=position),
                GridPosition(x=x, y=y),
                Velocity(),
                Health(max_amount=50),  # У врага меньше здоровья чем у игрока
                Attack(damage=5),
                Animation(frames=frames, frame_time=300),
                Render(
                    sprite=sprite,
                    scale=1.0,
                    layer=1
                ),
                EnemyTag(),
                Collider(position=position)
            ]
        )

    def create_health_potion(self, x, y) -> EntityId:
        walkable = self._get_walkable_tiles()
        if not walkable:
            return None
        if x is None or y is None or (x, y) not in walkable:
            x, y = random.choice(walkable)

        position = pygame.Vector2(x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)

        sprite = self.assets.get_sprite('items/flask.png')
        return self.ecs.create_entity([
            Position(position=position),
            GridPosition(x=x, y=y),
            Render(sprite=sprite, scale=1.0, layer=1),
            Item(name='Health Potion'),
            HealEffect(amount=30)
        ])

    def create_bomb_pickup(self, x=None, y=None) -> EntityId:
        walkable = self._get_walkable_tiles()
        if not walkable:
            return None
        if x is None or y is None or (x, y) not in walkable:
            x, y = random.choice(walkable)

        position = pygame.Vector2(x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)
        sprite = self.assets.get_sprite('items/coin_1.png')  # Placeholder sprite

        return self.ecs.create_entity([
            Position(position=position),
            GridPosition(x=x, y=y),
            Render(sprite=sprite, scale=1.0, layer=1),
            Item(name='Bomb'),
        ])
