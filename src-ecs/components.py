from dataclasses import dataclass, field
import math
import settings
import pygame
from typing import List, Optional, Dict, Any, Tuple


class PlayerTag:
    pass


@dataclass(slots=True)
class ColliderComponent:
    position: pygame.Vector2
    radius: float = 0

    def distance(self, other: 'ColliderComponent'):
        return math.sqrt((self.position.x - other.position.x) ** 2 + (self.position.y - other.position.y) ** 2)

    def is_intersecting(self, other: 'ColliderComponent'):
        return self.distance(other) <= self.radius + other.radius


@dataclass(slots=True)
class VelocityComponent:
    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))


@dataclass(slots=True)
class DamageOnContactComponent:
    damage: int
    die_on_contact: bool = True


@dataclass(slots=True)
class HealthComponent:
    max_amount: int
    amount: int = field(default=None)

    def __post_init__(self):
        if self.amount is None:
            self.amount = self.max_amount

    def apply_damage(self, damage: int):
        self.amount = max(0, self.amount - damage)


@dataclass(slots=True)
class TilemapComponent:
    cell_size: int = settings.TileMap.TILE_SIZE
    map_width: int = field(default_factory=lambda: settings.TileMap.MAP_WIDTH)
    map_height: int = field(default_factory=lambda: settings.TileMap.MAP_HEIGHT)
    template_path: str = field(default_factory=lambda: settings.TileMap.TEMPLATE_PATH)
    tiles: List[str] = field(default_factory=list)
    is_rendered: bool = False
    cached_tilemap: List[List[Dict[str, Any]]] = field(default_factory=list)  # Will store tile type and variant
    scaled_cache: Dict[Tuple[int, int], pygame.Surface] = field(default_factory=dict)  # Cache for scaled sprites

    def regenerate(self):
        """Очищает кэш карты, что приведет к её перегенерации"""
        self.cached_tilemap = []
        self.scaled_cache.clear()  # Очищаем кэш масштабированных спрайтов

    def get_scaled_sprite(self, sprite: pygame.Surface, size: int) -> pygame.Surface:
        """Получает масштабированный спрайт из кэша или создает новый"""
        cache_key = (id(sprite), size)
        if cache_key not in self.scaled_cache:
            self.scaled_cache[cache_key] = pygame.transform.scale(sprite, (size, size))
        return self.scaled_cache[cache_key]


@dataclass(slots=True)
class TileComponent:
    tile_type: int
    rect: pygame.Rect = None


@dataclass(slots=True)
class RenderTargetComponent:
    surface: pygame.Surface = None
    assets: Optional['AssetManager'] = None


@dataclass(slots=True)
class PositionComponent:
    position: pygame.Vector2


@dataclass(slots=True)
class RenderComponent:
    sprite: Optional[pygame.Surface] = None
    rect: Optional[pygame.Rect] = None
    color: pygame.Color = field(
        default_factory=lambda: pygame.Color(255, 255, 255))
    scale: float = 1.0

    def get_width(self) -> int:
        if self.sprite:
            return int(self.sprite.get_width() * self.scale)
        return 0

    def get_height(self) -> int:
        if self.sprite:
            return int(self.sprite.get_height() * self.scale)
        return 0
