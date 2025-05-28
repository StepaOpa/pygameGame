from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId


def velocity_system(velocity: VelocityComponent, collider: ColliderComponent):
    collider.x += velocity.speed_x
    collider.y += velocity.speed_y


def damage_on_contact_system(entity_id: EntityId,
                             ecs: EntityComponentSystem,
                             damage_on_contact: DamageOnContactComponent,
                             collider: ColliderComponent):
    for enemy_id, (enemy_health, enemy_collider) in ecs.get_entities_with_components(HealthComponent,
                                                                                     ColliderComponent):
        if collider.is_intersecting(enemy_collider):
            enemy_health.apply_damage(damage_on_contact.damage)
            if damage_on_contact.die_on_contact:
                ecs.remove_entity(entity_id)
            return


def death_system(entity_id: EntityId, health: HealthComponent, ecs: EntityComponentSystem):
    if health.amount <= 0:
        ecs.remove_entity(entity_id)
