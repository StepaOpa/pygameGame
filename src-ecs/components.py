from dataclasses import dataclass, field
import math


@dataclass(slots=True)
class ColliderComponent:
    x: float
    y: float
    radius: float

    def distance(self, other: 'ColliderComponent'):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def is_intersecting(self, other: 'ColliderComponent'):
        return self.distance(other) <= self.radius + other.radius


@dataclass(slots=True)
class VelocityComponent:
    speed_x: float = 0.0
    speed_y: float = 0.0


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
