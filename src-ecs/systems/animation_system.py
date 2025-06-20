from components import *
from ecs_types import EntityId, System


class AnimationSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Animation, Render]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        anim: Animation
        render: Render
        anim, render = components

        delta_ms = ecs.get_variable('delta_ms') or 16
        anim.elapsed += delta_ms
        while anim.elapsed >= anim.frame_time:
            anim.elapsed -= anim.frame_time
            anim.current_frame += 1
            if anim.current_frame >= len(anim.frames):
                if anim.loop:
                    anim.current_frame = 0
                else:
                    anim.current_frame = len(anim.frames) - 1
                    if anim.destroy_on_end:
                        ecs.remove_entity(entity_id)
                        return
            render.sprite = anim.frames[anim.current_frame] 