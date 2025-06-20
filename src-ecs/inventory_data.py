from dataclasses import dataclass, field


@dataclass
class PersistentStorage:
    """Хранилище, переживающее смену сцен/уровней.
    Сейчас содержит только список названий предметов инвентаря.
    """
    inventory: list[str] = field(default_factory=list)


GLOBAL_STORAGE = PersistentStorage()

ITEM_SPRITE_MAP: dict[str, str] = {
    'Health Potion': 'items/flask.png',
    'Bomb': 'Items/coin_1.png',
}
