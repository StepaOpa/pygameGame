from dataclasses import dataclass, field
import math
import settings
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
        return self.distance(other) <= self.radius + other.radius


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
