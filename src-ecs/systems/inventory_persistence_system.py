from components import *
from ecs_types import EntityId, System
from inventory_data import GLOBAL_STORAGE


class InventoryPersistenceSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Inventory, PlayerTag]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        inv, _ = components

        GLOBAL_STORAGE.inventory = [item.name for item in inv.items] 