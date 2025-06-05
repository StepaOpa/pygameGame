from dataclasses import dataclass
from typing import Any, Type
from abc import ABC, abstractmethod

EntityId = str
Component = object


class System(ABC):
    def __init__(self):
        self.required_components = []
    
    @abstractmethod
    def update(self, entity_id: EntityId, components: list[Component], ecs: Any = None):
        """Выполняет обновление состояния для конкретной сущности"""
        pass


@dataclass
class StoredSystem:
    system: System
    components: list[Type[Component]]  # Список требуемых компонентов
    has_ecs_argument: bool
