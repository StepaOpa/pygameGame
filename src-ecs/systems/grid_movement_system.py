from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId, System


class GridMovementSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, PlayerTag]

        self.walkable_tiles: dict[tuple[int, int], bool] = {}
        self.is_cache_dirty = True

    def _update_walkable_cache(self, ecs: EntityComponentSystem):
        self.walkable_tiles.clear()
        for _, (grid_pos, tile) in ecs.get_entities_with_components(GridPosition, TileComponent):
            self.walkable_tiles[(grid_pos.x, grid_pos.y)] = tile.walkable
        self.is_cache_dirty = False

    def is_walkable(self, x: int, y: int, ecs: EntityComponentSystem) -> bool:
        if self.is_cache_dirty:
            self._update_walkable_cache(ecs)
        return self.walkable_tiles.get((x, y), False)

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        grid_position, _ = components
        pass 