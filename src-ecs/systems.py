from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId
import random
import pygame
from map_generator import generate_tilemap_from_template, render_tilemap
import debug


def velocity_system(velocity: VelocityComponent, collider: ColliderComponent, position: PositionComponent):
    position.position += velocity.velocity
    collider.position = position.position.copy()


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


def tilemap_cache_system(tilemap: TilemapComponent):
    if len(tilemap.cached_tilemap) == 0:
        tilemap.cached_tilemap = generate_tilemap_from_template(tilemap.template_path)
        if debug.IS_DEBUG:
            print('Tilemap_cache_system done. Tilemap cached')


def tilemap_system(tilemap: TilemapComponent, render_target: RenderTargetComponent):
    render_tilemap(tilemap, render_target.surface, render_target.assets)


def render_system(position: PositionComponent, render: RenderComponent, render_target: RenderTargetComponent):
    surface = render_target.surface
    if render.sprite:
        original_size = render.sprite.get_size()
        new_width = int(original_size[0] * render.scale)
        new_height = int(original_size[1] * render.scale)
        scaled_sprite = pygame.transform.smoothscale(
            render.sprite,
            (new_width, new_height)
        )
        surface.blit(scaled_sprite, position.position)
    else:
        surface.blit(render.sprite, position.position)


def input_system(velocity: VelocityComponent, player_tag: PlayerTag, ecs: EntityComponentSystem):
    keys = pygame.key.get_pressed()
    speed = settings.PlayerSettings.SPEED

    # Обработка движения
    movement = pygame.Vector2(0, 0)

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        movement.x -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        movement.x += 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        movement.y -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        movement.y += 1

    if movement.length() > 0:
        movement = movement.normalize() * speed

    velocity.velocity = movement

    # Обработка перегенерации карты по нажатию R
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_r]:
        for _, tilemap in ecs.get_entities_with_components(TilemapComponent):
            tilemap.regenerate()

