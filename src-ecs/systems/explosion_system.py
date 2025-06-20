from components import *
from ecs_types import EntityId, System
import pygame
import settings


class ExplosionSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Explosion, GridPosition, Position]

    def update(self, eid: EntityId, comps: list[Component], ecs=None):
        expl, grid_pos, pos = comps

        if expl.frames_created:
            return

        render_target = ecs.get_variable('render_target')
        assets = render_target.assets if render_target else None
        frames: list[pygame.Surface] = []
        if assets:
            for i in range(1, 10):
                frames.append(assets.get_sprite(f'Effects/teleport/teleport_{i}.png'))
        if not frames:
            return

        tile = settings.TileMap.TILE_SIZE
        target_size = (tile * 3, tile * 3)
        scaled = [pygame.transform.smoothscale(f, target_size) for f in frames]

        ecs._components[Render][eid] = Render(sprite=scaled[0], scale=1.0, layer=2)
        ecs._components[Animation][eid] = Animation(frames=scaled, frame_time=100, loop=False, destroy_on_end=True)

        expl.frames_created = True 