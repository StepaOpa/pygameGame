from dataclasses import dataclass
from ecs import Component, Entity
import pygame


@dataclass
class Transform(Component):
    x: float
    y: float
    rotation: float = 0.0
    scale: tuple[float, float] = (1, 1)

    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Sprite(Component):
    image: pygame.Surface
    rect: pygame.Rect = None


@dataclass
class Physics(Component):
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    сollider: pygame.Rect = None
    gravity: float = 0.0


@dataclass
class PlayerController(Component):
    speed: float = 200.0


@dataclass
class EnemyAI(Component):
    target: Entity = None
    speed: float = 100.0


@dataclass
class Camera(Component):
    surface: pygame.Surface
    display_surface: pygame.Surface


@dataclass
class PlayerController(Component):
    speed: float = 200.0
