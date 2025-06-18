from dataclasses import dataclass, field
import math
from assets import AssetManager
import pygame
from typing import List, Optional, Dict, Any, Tuple
from abc import ABC


class Component(ABC):
    """Базовый класс для всех компонентов"""
    pass


@dataclass(slots=True)
class PlayerTag(Component):
    pass


@dataclass(slots=True)
class TurnComponent(Component):
    """Компонент для отслеживания состояния хода"""
    is_player_turn: bool = True
    player_moved: bool = False  # Флаг, показывающий, сделал ли игрок ход
    turn_count: int = 0  # Счетчик ходов игрока


@dataclass(slots=True)
class EnemyTag(Component):
    pass


@dataclass(slots=True)
class Collider(Component):
    position: pygame.Vector2
    radius: float = 0

    def distance(self, other: 'Collider'):
        return math.sqrt((self.position.x - other.position.x) ** 2 + (self.position.y - other.position.y) ** 2)

    def is_intersecting(self, other: 'Collider'):
        return self.distance(other) <= (self.radius + other.radius)


@dataclass(slots=True)
class Velocity(Component):
    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))


@dataclass(slots=True)
class DamageOnContact(Component):
    damage: int
    die_on_contact: bool = True


@dataclass(slots=True)
class Health(Component):
    max_amount: int
    amount: int = field(default=None)

    def __post_init__(self):
        if self.amount is None:
            self.amount = self.max_amount

    def apply_damage(self, damage: int):
        self.amount = max(0, self.amount - damage)


@dataclass(slots=True)
class TileComponent(Component):
    tile_type: str
    walkable: bool
    variant: str = '0'


@dataclass(slots=True)
class GridPosition(Component):
    x: int
    y: int


@dataclass(slots=True)
class Tile(Component):
    tile_type: int
    rect: pygame.Rect = None


@dataclass(slots=True)
class RenderTarget(Component):
    surface: pygame.Surface = None
    assets: Optional['AssetManager'] = None


@dataclass(slots=True)
class Position(Component):
    position: pygame.Vector2


@dataclass(slots=True)
class Render(Component):
    sprite: Optional[pygame.Surface] = None
    rect: Optional[pygame.Rect] = None
    color: pygame.Color = field(
        default_factory=lambda: pygame.Color(255, 255, 255))
    scale: float = 1.0
    layer: int = 0

    def get_width(self) -> int:
        if self.sprite:
            return int(self.sprite.get_width() * self.scale)
        return 0

    def get_height(self) -> int:
        if self.sprite:
            return int(self.sprite.get_height() * self.scale)
        return 0


# --- Бой ----------------------------------------------------------------


@dataclass(slots=True)
class Attack(Component):
    """Сколько урона наносит сущность при атаке (bump-to-attack)."""
    damage: int = 1


# --- Инвентарь ----------------------------------------------------------


@dataclass(slots=True)
class InventoryItem:
    name: str
    sprite: pygame.Surface


@dataclass(slots=True)
class Inventory(Component):
    items: list[InventoryItem] = field(default_factory=list)
    capacity: int = 10


@dataclass(slots=True)
class Item(Component):
    name: str


@dataclass(slots=True)
class HealEffect(Component):
    amount: int = 20


# --- Бомбы --------------------------------------------------------------


@dataclass(slots=True)
class Bomb(Component):
    turns_left: int = 3  # ходов до взрыва
    radius: int = 1  # расстояние по манхэттену
    damage: int = 25
    last_turn_processed: int = -1  # вспомогательное поле, не сериализуется


# --- Анимации -----------------------------------------------------------


@dataclass(slots=True)
class Animation(Component):
    frames: list[pygame.Surface]
    frame_time: int = 100  # мс на кадр
    loop: bool = True
    destroy_on_end: bool = False  # уничтожить сущность после завершения анимации (если loop=False)
    elapsed: int = 0
    current_frame: int = 0
