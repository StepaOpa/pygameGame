from components import *
from ecs_types import EntityId, System
from sound_engine import SoundEngine


class DeathSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Health]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        health = components[0]
        if health.amount <= 0:
            if ecs.get_component(entity_id, EnemyTag) is not None:
                try:
                    SoundEngine.get().play('enemy_die', volume=0.6)
                except RuntimeError:
                    pass
            elif ecs.get_component(entity_id, PlayerTag) is not None:
                try:
                    SoundEngine.get().play('player_die', volume=0.8)
                except RuntimeError:
                    pass

            ecs.remove_entity(entity_id) 