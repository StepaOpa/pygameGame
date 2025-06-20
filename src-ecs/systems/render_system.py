from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId, System
import pygame
import settings


class RenderSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Position, Render]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        pass

    def draw_all(self, ecs: EntityComponentSystem):
        render_target = ecs.get_variable('render_target')
        if not render_target:
            return

        surface = render_target.surface
        
        renderable_entities = []
        for entity_id, (pos, render) in ecs.get_entities_with_components(Position, Render):
            is_grid_aligned = (
                ecs.get_component(entity_id, GridPosition) is not None or
                ecs.get_component(entity_id, TileComponent) is not None
            )
            renderable_entities.append((render.layer, pos, render, is_grid_aligned))

        renderable_entities.sort(key=lambda e: e[0])

        for layer, position, render, is_grid_aligned in renderable_entities:
            if render.sprite:
                original_size = render.sprite.get_size()
                new_width = int(original_size[0] * render.scale)
                new_height = int(original_size[1] * render.scale)
                scaled_sprite = pygame.transform.smoothscale(
                    render.sprite,
                    (new_width, new_height)
                )
                
                if is_grid_aligned:
                    offset_x = (settings.TileMap.TILE_SIZE - new_width) // 2
                    offset_y = (settings.TileMap.TILE_SIZE - new_height) // 2
                else:
                    offset_x = -new_width // 2
                    offset_y = -new_height // 2
                render_pos = (position.position.x + offset_x, position.position.y + offset_y)
                surface.blit(scaled_sprite, render_pos) 