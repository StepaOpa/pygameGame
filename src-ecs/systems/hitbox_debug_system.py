from components import *
from ecs_types import EntityId, System
import pygame
import debug


class HitboxDebugSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Position, Hitbox]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        pass
    
    def draw_debug(self, ecs):
        if not debug.IS_DEBUG or not debug.SHOW_HITBOXES:
            return
            
        render_target = ecs.get_variable('render_target')
        if not render_target or not render_target.surface:
            return
            
        surface = render_target.surface
        
        for entity_id, (position, hitbox) in ecs.get_entities_with_components(Position, Hitbox):
            rect = hitbox.get_rect(position)
            
            color = pygame.Color(255, 255, 255, 128)
            
            try:
                ecs.get_component(entity_id, PlayerTag)
                color = pygame.Color(0, 255, 0, 128)
            except KeyError:
                pass
            try:
                ecs.get_component(entity_id, EnemyTag)
                color = pygame.Color(255, 0, 0, 128)
            except KeyError:
                pass
            try:
                ecs.get_component(entity_id, Fireball)
                color = pygame.Color(255, 165, 0, 128)
            except KeyError:
                pass
            
            pygame.draw.rect(surface, color, rect, 2) 