from components import *
from ecs_types import EntityId, System
import pygame
import debug
import settings
from sound_engine import SoundEngine


class BombSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Bomb, GridPosition]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        bomb, grid_pos = components

        turn_cmp = None
        for _, (turn,) in ecs.get_entities_with_components(TurnComponent):
            turn_cmp = turn
            break
        if turn_cmp is None:
            return

        if bomb.state == 'ticking':
            if turn_cmp.turn_count - bomb.planted_turn >= bomb.fuse_turns:
                bomb.state = 'exploding'
                try:
                    SoundEngine.get().play('explosion', volume=0.8)
                except RuntimeError:
                    pass
                ecs._components[Explosion][entity_id] = Explosion()
        elif bomb.state == 'exploding':
            for tid, (t_grid, t_hp) in ecs.get_entities_with_components(GridPosition, Health):
                if max(abs(t_grid.x - grid_pos.x), abs(t_grid.y - grid_pos.y)) <= bomb.radius:
                    t_hp.apply_damage(bomb.damage)

            if Bomb in ecs._components and entity_id in ecs._components[Bomb]:
                del ecs._components[Bomb][entity_id]

    def draw_debug(self, ecs):
        if not (hasattr(debug, 'IS_DEBUG') and debug.IS_DEBUG):
            return

        render_target = ecs.get_variable('render_target')
        if not render_target or not render_target.surface:
            return

        tile_sz = settings.TileMap.TILE_SIZE
        surf = render_target.surface
        for _, (bomb, gpos) in ecs.get_entities_with_components(Bomb, GridPosition):
            for dx in range(-bomb.radius, bomb.radius + 1):
                for dy in range(-bomb.radius, bomb.radius + 1):
                    if max(abs(dx), abs(dy)) <= bomb.radius:
                        rect = pygame.Rect((gpos.x + dx) * tile_sz, (gpos.y + dy) * tile_sz, tile_sz, tile_sz)
                        pygame.draw.rect(surf, pygame.Color(255, 0, 0, 100), rect, 1) 