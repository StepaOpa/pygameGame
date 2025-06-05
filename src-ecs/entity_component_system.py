import inspect
from typing import Callable, Type, Any, Iterator

from ecs_types import EntityId, Component, StoredSystem, System
from unique_id import UniqueIdGenerator


class EntityComponentSystem:
    def __init__(self, on_create: Callable[[EntityId, list[Component]], None] = None,
                 on_remove: Callable[[EntityId], None] = None):
        """
        :param on_create:
        Хук, отрабатывающий при создании сущности,
        например может пригодиться, если сервер сообщает клиентам о появлении новых сущностей

        :param on_remove:
        Хук, отрабатывающий перед удалением сущности
        """

        self._systems: list[StoredSystem] = []
        self._components: dict[Type[Component], dict[EntityId, Component]] = {}
        self._entities: list[EntityId] = []
        self._vars = {}
        self.on_create = on_create
        self.on_remove = on_remove

    def _unsafe_get_component(self, entity_id: EntityId, component_class: Type[Component]) -> Component:
        """
        Возвращает компонент сущности с типом переданного класса component_class
        Кидает KeyError если сущность не существует или не имеет такого компонента
        """
        return self._components[component_class][entity_id]

    def init_component(self, component_class: Type[Component]) -> None:
        """
        Инициализация класса компонента. Следует вызвать до создания сущностей
        """
        self._components[component_class] = {}

    def add_variable(self, variable_name: str, variable_value: Any) -> None:
        """
        Инициализация переменной. Далее может быть запрошена любой системой.
        """
        self._vars[variable_name] = variable_value

    def get_variable(self, variable_name: str) -> Any:
        return self._vars.get(variable_name)

    def add_system(self, system: System) -> None:
        """
        Добавление системы в ECS
        """
        stored = StoredSystem(
            system=system,
            components=system.required_components,
            has_ecs_argument=True  # Всегда передаем ECS в системы
        )
        self._systems.append(stored)

    def get_system(self, system_class: Type[System]) -> System | None:
        """
        Получение инстанса системы по её классу
        """
        for stored in self._systems:
            if isinstance(stored.system, system_class):
                return stored.system
        return None

    def create_entity(self, components: list[Component], entity_id=None) -> EntityId:
        """
        Создание сущности на основе списка его компонентов
        Можно задавать свой entity_id но он обязан быть уникальным
        """
        if entity_id is None:
            entity_id = str(len(self._entities))

        for component in components:
            self._components[component.__class__][entity_id] = component
        self._entities.append(entity_id)

        if self.on_create:
            self.on_create(entity_id, components)

        return entity_id

    def get_entity_ids_with_components(self, *component_classes) -> set[EntityId]:
        """
        Получить все entity_id у которых есть каждый из компонентов, указанных в component_classes
        """
        if not component_classes:
            return set(self._entities)

        entities = set.intersection(*[set(self._components[component_class].keys())
                                    for component_class in component_classes])
        return entities

    def get_entities_with_components(self, *component_classes) -> Iterator[tuple[EntityId, list[Component]]]:
        """
        Получить все entity_id вместе с указанными компонентами
        """
        for entity_id in self.get_entity_ids_with_components(*component_classes):
            components = tuple(self._unsafe_get_component(entity_id, component_class)
                             for component_class in component_classes)
            yield entity_id, components

    def update(self) -> None:
        """
        Вызывает все системы.
        Следует вызывать в игровом цикле.
        """
        for stored_system in self._systems:
            for entity_id in self.get_entity_ids_with_components(*stored_system.components):
                components = [self._unsafe_get_component(entity_id, component_class)
                            for component_class in stored_system.components]
                
                if stored_system.has_ecs_argument:
                    stored_system.system.update(entity_id, components, self)
                else:
                    stored_system.system.update(entity_id, components)

    def remove_entity(self, entity_id: EntityId):
        """
        Удаляет сущность
        """
        if self.on_remove is not None:
            self.on_remove(entity_id)
        for components in self._components.values():
            components.pop(entity_id, None)
        self._entities.remove(entity_id)

    def get_component(self, entity_id: EntityId, component_class: Type[Component]):
        """
        :return
        Возвращает компонент сущности с типом переданного класса component_class
        Возвращает None если сущность не существует или не имеет такого компонента
        """
        return self._components[component_class].get(entity_id, None)

    def get_components(self, entity_id: EntityId, component_classes):
        """
        :return
        Возвращает требуемые компоненты сущности.
        Возвращает None если сущность не существует или не имеет всех этих компонентов
        """
        try:
            return tuple(self._unsafe_get_component(entity_id, component_class)
                        for component_class in component_classes)
        except KeyError:
            return None
