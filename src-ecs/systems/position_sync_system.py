from components import *
from ecs_types import EntityId, System
import settings


class PositionSyncSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, Position]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        grid_position, position = components
        target_x = grid_position.x * settings.TileMap.TILE_SIZE
        target_y = grid_position.y * settings.TileMap.TILE_SIZE
        
        position.position.x = target_x
        position.position.y = target_y 