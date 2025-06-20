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
    player_moved: bool = False
    turn_count: int = 0


@dataclass(slots=True)
class EnemyTag(Component):
    pass


@dataclass(slots=True)
class FlyingEnemyTag(Component):
    """Отмечает врагов, которые ходят каждый ход игрока."""
    pass


@dataclass(slots=True)
class Velocity(Component):
    velocity: pygame.Vector2 = field(
        default_factory=lambda: pygame.Vector2(0, 0))


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
    sprite_path: str = ""


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
    """Бомба со 'state-machine'.

    Состояния:
        • ticking   – ещё тикает.
        • exploding – перешла во взрыв (обработка урона и спрайта).
    """
    planted_turn: int = 0
    fuse_turns: int = 3
    radius: int = 1
    damage: int = 25
    state: str = 'ticking'   # 'ticking' ,  'exploding'


# --- Маркер для системы взрыва ---------------------------------------


@dataclass(slots=True)
class Explosion(Component):
    """Помечает сущность, у которой надо отрисовать/проиграть взрыв."""
    frames_created: bool = False


# --- Анимации -----------------------------------------------------------


@dataclass(slots=True)
class Animation(Component):
    frames: list[pygame.Surface]
    frame_time: int = 100
    loop: bool = True
    destroy_on_end: bool = False
    elapsed: int = 0
    current_frame: int = 0


@dataclass(slots=True)
class WizardTag(Component):
    """Тег для обозначения врага-волшебника (Wizard)."""
    pass


@dataclass(slots=True)
class Fireball(Component):
    """Снаряд, летящий по прямой к цели в пиксельных координатах.
    velocity_x, velocity_y — скорость в пикселях за обновление.
    """
    velocity_x: float
    velocity_y: float
    damage: int = 15


@dataclass(slots=True)
class WizardState(Component):
    last_shot_turn: int = -2


@dataclass(slots=True)
class Hitbox(Component):
    """Прямоугольная область для определения столкновений.
    offset_x, offset_y — смещение от позиции сущности.
    width, height — размеры хитбокса в пикселях.
    """
    offset_x: float = 0.0
    offset_y: float = 0.0
    width: float = 16.0
    height: float = 16.0

    def get_rect(self, position: 'Position') -> pygame.Rect:
        """Возвращает pygame.Rect хитбокса в мировых координатах."""
        return pygame.Rect(
            position.position.x + self.offset_x,
            position.position.y + self.offset_y,
            self.width,
            self.height
        )
