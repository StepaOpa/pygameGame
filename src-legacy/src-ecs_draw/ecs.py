from dataclasses import dataclass
from typing import Dict, Type, List, Set


class Component:
    pass


@dataclass
class Entity:
    id: int
    components: Dict[type[Component], Component]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.id == other.id
        return False


class System:
    def __init__(self, ecs: 'ECS'):
        self.ecs: ECS = ecs

    def update(self, delta_time):
        pass


class ECS:
    def __init__(self):
        self.entities = {}
        self.next_entity_id = 0
        self.systems: List[System] = []

    def create_entity(self) -> Entity:
        entity = Entity(self.next_entity_id, {})
        self.entities[self.next_entity_id] = entity
        self.next_entity_id += 1
        return entity

    def add_component(self, entity: Entity, component: Component):
        entity.components[type(component)] = component
        print(f"Added {type(component).__name__} to entity {entity.id}")
        print(entity.components)

    def add_system(self, system: System):
        self.systems.append(system)

    def get_entities_with(self, *components_to_find: List[Component]) -> Set[Entity]:
        entities = set()
        for entity in self.entities.values():
            if all(isinstance(entity.components.get(component_type), component_type) for component_type in components_to_find):
                entities.add(entity)
        return entities

    def update(self, delta_time: float):
        for system in self.systems:
            system.update(delta_time)
