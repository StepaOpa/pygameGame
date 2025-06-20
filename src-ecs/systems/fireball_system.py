from components import *
from ecs_types import EntityId, System
import debug
import settings
from sound_engine import SoundEngine


class FireballSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Fireball, Position, Hitbox]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        fireball, position, hitbox = components

        position.position.x += fireball.velocity_x
        position.position.y += fireball.velocity_y

        map_pixel_width = settings.TileMap.MAP_WIDTH * settings.TileMap.TILE_SIZE
        map_pixel_height = settings.TileMap.MAP_HEIGHT * settings.TileMap.TILE_SIZE
        
        margin = 4
        if (
            position.position.x < -margin or position.position.y < -margin or
            position.position.x >= map_pixel_width + margin or position.position.y >= map_pixel_height + margin
        ):
            if debug.IS_DEBUG:
                print(f"Фаербол удален за границей карты: pos=({position.position.x:.1f}, {position.position.y:.1f}), "
                      f"границы=(0, 0, {map_pixel_width}, {map_pixel_height})")
            ecs.remove_entity(entity_id)
            return

        fireball_rect = hitbox.get_rect(position)

        for player_id, (player_pos, player_hitbox, _) in ecs.get_entities_with_components(Position, Hitbox, PlayerTag):
            player_rect = player_hitbox.get_rect(player_pos)
            
            if fireball_rect.colliderect(player_rect):
                player_health = ecs.get_component(player_id, Health)
                if player_health:
                    player_health.apply_damage(fireball.damage)
                    try:
                        SoundEngine.get().play('player_hurt', volume=0.7)
                    except RuntimeError:
                        pass
                if debug.IS_DEBUG:
                    print(f"Фаербол попал в игрока: урон {fireball.damage}")
                ecs.remove_entity(entity_id)
                return 