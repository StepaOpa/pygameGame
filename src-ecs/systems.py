from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId
import random
import pygame


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
        tilemap.cached_tilemap = [
            [None] * tilemap.map_height for _ in range(tilemap.map_width)]
        for x in range(tilemap.map_width):
            for y in range(tilemap.map_height):
                tile = random.choice(
                    list(settings.TileMap.COLORS.values()))
                tilemap.cached_tilemap[x][y] = pygame.Color(tile)
    else:
        return


def tilemap_system(tilemap: TilemapComponent, render_target: RenderTargetComponent):
    surface = render_target.surface
    cell_size = tilemap.cell_size
    for x in range(tilemap.map_width):
        for y in range(tilemap.map_height):
            tile = tilemap.cached_tilemap[x][y]
            pygame.draw.rect(surface, tile, pygame.Rect(
                x * cell_size, y * cell_size, cell_size, cell_size))


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


def input_system(velocity: VelocityComponent, player_tag: PlayerTag):
    keys = pygame.key.get_pressed()
    speed = settings.PlayerSettings.SPEED

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


def get_tile_type_by_color(color):
    color_map = {
        (0, 0, 0, 255): 'empty',
        (0, 255, 0, 255): 'wall',
        (143, 86, 59, 255): 'floor',
    }
    return color_map.get(color, 'empty')

def get_tile_variant(x, y, pixel_array, width, height):
    def is_wall(nx, ny):
        if 0 <= nx < width and 0 <= ny < height:
            return get_tile_type_by_color(pixel_array[nx, ny]) == 'wall'
        return False

    up = is_wall(x, y-1)
    down = is_wall(x, y+1)
    left = is_wall(x-1, y)
    right = is_wall(x+1, y)

    if not up and not left:
        return 'top_left_corner'
    if not up and not right:
        return 'top_right_corner'
    if not down and not left:
        return 'bottom_left_corner'
    if not down and not right:
        return 'bottom_right_corner'
    if not up:
        return 'top'
    if not down:
        return 'bottom'
    if not left:
        return 'left'
    if not right:
        return 'right'
    return 'center'

def generate_level_from_template(template_path, tile_collection, surface):
    template = pygame.image.load(template_path).convert_alpha()
    width, height = template.get_size()
    pixel_array = pygame.PixelArray(template)

    for x in range(width):
        for y in range(height):
            color = template.unmap_rgb(pixel_array[x, y])
            tile_type = get_tile_type_by_color(color)
            if tile_type == 'wall':
                variant = get_tile_variant(x, y, pixel_array, width, height)
                tile_sprite = tile_collection['walls'][variant]
                surface.blit(tile_sprite, (x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE))
            elif tile_type == 'floor':
                tile_sprite = tile_collection['floor']
                surface.blit(tile_sprite, (x * settings.TileMap.TILE_SIZE, y * settings.TileMap.TILE_SIZE))

    del pixel_array