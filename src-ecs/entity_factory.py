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
from inventory_data import GLOBAL_STORAGE, ITEM_SPRITE_MAP


class EntityFactory:
    def __init__(self, ecs: EntityComponentSystem, assets: AssetManager, display: pygame.Surface):
        self.ecs = ecs
        self.assets = assets
        self.display = display

    def create_map(self) -> None:
        return generate_tile_entities_from_template(settings.TileMap.TEMPLATE_PATH, self)

    def create_player(self, x, y) -> EntityId:
        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)
        frames = []
        for i in range(4):
            path = f'Player/idle/idle_{i}.png'
            frames.append(self.assets.get_sprite(path))
        sprite = frames[0]

        player_id = self.ecs.create_entity([
            Position(position=position),
            GridPosition(x=x, y=y),
            Velocity(),
            Health(max_amount=100),
            Attack(damage=10),
            Inventory(),
            Animation(frames=frames, frame_time=200),
            Render(sprite=sprite, scale=1.0, layer=1),
            PlayerTag(),
            Hitbox(offset_x=0, offset_y=0, width=16, height=16),
        ])

        if GLOBAL_STORAGE.inventory:
            inv_comp = self.ecs.get_component(player_id, Inventory)
            if inv_comp is not None:
                for item_name in GLOBAL_STORAGE.inventory:
                    sprite_path = ITEM_SPRITE_MAP.get(item_name)
                    if sprite_path is None:
                        continue
                    sprite_item = self.assets.get_sprite(sprite_path)
                    inv_comp.items.append(InventoryItem(
                        name=item_name, sprite=sprite_item, sprite_path=sprite_path))

        return player_id

    def create_tile(self, x: int, y: int, tile_type: str, variant: str, walkable: bool) -> EntityId:

        if tile_type == 'floor':
            sprite = self.assets.get_sprite(variant)
        else:
            sprite = self.assets.get_tile_sprite(variant)

        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)

        return self.ecs.create_entity(
            [
                Position(position=position),
                GridPosition(x=x, y=y),
                Render(sprite=sprite, scale=settings.TileMap.TILE_SIZE/16, layer=0),
                TileComponent(tile_type=tile_type,
                              variant=variant, walkable=walkable)
            ]
        )

    def _get_walkable_tiles(self) -> List:
        walkable_tiles = []
        for entity_id, (grid_pos, tile) in self.ecs.get_entities_with_components(GridPosition, TileComponent):
            if tile.walkable:
                walkable_tiles.append((grid_pos.x, grid_pos.y))
        return walkable_tiles

    def create_enemy(self) -> EntityId:
        walkable_tiles = self._get_walkable_tiles()
        if not walkable_tiles:
            return None

        x, y = random.choice(walkable_tiles)
        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)

        frames = []
        for i in range(3):
            path = f'Enemies/Vampire/vampire_idle_{i}.png'
            frames.append(self.assets.get_sprite(path))
        sprite = frames[0]

        return self.ecs.create_entity(
            [
                Position(position=position),
                GridPosition(x=x, y=y),
                Velocity(),
                Health(max_amount=50),
                Attack(damage=5),
                Animation(frames=frames, frame_time=300),
                Render(
                    sprite=sprite,
                    scale=1.0,
                    layer=1
                ),
                EnemyTag(),
            ]
        )

    def create_health_potion(self, x, y) -> EntityId:
        walkable = self._get_walkable_tiles()
        if not walkable:
            return None
        if x is None or y is None or (x, y) not in walkable:
            x, y = random.choice(walkable)

        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)

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

        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)
        sprite = self.assets.get_sprite('Items/bomb.png')

        return self.ecs.create_entity([
            Position(position=position),
            GridPosition(x=x, y=y),
            Render(sprite=sprite, scale=1.0, layer=1),
            Item(name='Bomb'),
        ])

    def create_flying_enemy(self) -> EntityId:
        walkable_tiles = self._get_walkable_tiles()
        if not walkable_tiles:
            return None

        x, y = random.choice(walkable_tiles)
        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)

        frames = []
        for i in range(4):
            path = f'Enemies/Skull/skull_{i}.png'
            frames.append(self.assets.get_sprite(path))
        sprite = frames[0]

        return self.ecs.create_entity([
            Position(position=position),
            GridPosition(x=x, y=y),
            Velocity(),
            Health(max_amount=30),
            Attack(damage=7),
            Animation(frames=frames, frame_time=150),
            Render(sprite=sprite, scale=1.0, layer=1),
            EnemyTag(),
            FlyingEnemyTag(),
        ])

    def create_wizard_enemy(self) -> EntityId:
        """Создаёт врага-волшебника. Строго наземный (не Flying)."""
        walkable_tiles = self._get_walkable_tiles()
        if not walkable_tiles:
            return None

        x, y = random.choice(walkable_tiles)
        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)

        frames = []
        for i in range(4):
            path = f'Enemies/Wizard/Wizard{i}.png'
            frames.append(self.assets.get_sprite(path))
        sprite = frames[0]

        return self.ecs.create_entity([
            Position(position=position),
            GridPosition(x=x, y=y),
            Velocity(),
            Health(max_amount=40),
            Attack(damage=8),
            Animation(frames=frames, frame_time=200),
            Render(sprite=sprite, scale=1.0, layer=1),
            EnemyTag(),
            WizardTag(),
            WizardState(),
        ])

    def create_exit_tile(self, x: int, y: int) -> EntityId:
        """Создаёт тайл выхода (лестницу) на указанных координатах.
        Если на клетке уже есть тайл (пол), заменяем его спрайт/тип, чтобы не создавать дубликат.
        """
        # Попытаемся найти существующий тайл на этих координатах
        for eid, (gpos, tile_comp, render) in self.ecs.get_entities_with_components(GridPosition, TileComponent, Render):
            if gpos.x == x and gpos.y == y:
                tile_comp.tile_type = 'stairs'
                tile_comp.variant = 'stairs'
                tile_comp.walkable = True
                render.sprite = self.assets.get_tile_sprite('stairs')
                return eid

        return self.create_tile(x, y, 'stairs', 'stairs', True)

    def create_explosion_effect(self, x: int, y: int) -> EntityId:
        """Создаёт визуальный эффект взрыва на клетке (x, y) без урона."""
        position = pygame.Vector2(
            x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE)
        return self.ecs.create_entity([
            Position(position=position),
            GridPosition(x=x, y=y),
            Explosion()
        ])
