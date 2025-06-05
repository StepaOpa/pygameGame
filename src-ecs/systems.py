from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId, System
import random
import pygame
import debug
import settings


class PositionSyncSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, Position]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        grid_position, position = components
        target_x = grid_position.x * settings.TileMap.TILE_SIZE
        target_y = grid_position.y * settings.TileMap.TILE_SIZE
        
        # Простое присваивание для движения по сетке. Можно заменить на lerp для плавности.
        position.position.x = target_x
        position.position.y = target_y


class DamageOnContactSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [DamageOnContact, Collider]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        damage_on_contact, collider = components
        for enemy_id, (enemy_health, enemy_collider) in ecs.get_entities_with_components(Health, Collider):
            if collider.is_intersecting(enemy_collider):
                enemy_health.apply_damage(damage_on_contact.damage)
                if damage_on_contact.die_on_contact:
                    ecs.remove_entity(entity_id)
                return


class DeathSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Health]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        health = components[0]
        if health.amount <= 0:
            ecs.remove_entity(entity_id)


class RenderSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Position, Render]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        # Этот метод больше не будет использоваться напрямую для отрисовки.
        # Вместо этого, мы будем вызывать новый метод draw_all() из игрового цикла.
        pass

    def draw_all(self, ecs: EntityComponentSystem):
        render_target = ecs.get_variable('render_target')
        if not render_target:
            return

        surface = render_target.surface
        
        # 1. Собрать все сущности для отрисовки
        renderable_entities = []
        for entity_id, (pos, render) in ecs.get_entities_with_components(Position, Render):
            renderable_entities.append((render.layer, pos, render))

        # 2. Отсортировать по слою
        renderable_entities.sort(key=lambda e: e[0])

        # 3. Отрисовать в правильном порядке
        for layer, position, render in renderable_entities:
            if render.sprite:
                original_size = render.sprite.get_size()
                new_width = int(original_size[0] * render.scale)
                new_height = int(original_size[1] * render.scale)
                scaled_sprite = pygame.transform.smoothscale(
                    render.sprite,
                    (new_width, new_height)
                )
                surface.blit(scaled_sprite, position.position)


class GridMovementSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, PlayerTag] # Пока двигается только игрок

        # Кэш для проходимых клеток для оптимизации
        self.walkable_tiles: dict[tuple[int, int], bool] = {}
        self.is_cache_dirty = True

    def _update_walkable_cache(self, ecs: EntityComponentSystem):
        self.walkable_tiles.clear()
        for _, (grid_pos, tile) in ecs.get_entities_with_components(GridPosition, TileComponent):
            self.walkable_tiles[(grid_pos.x, grid_pos.y)] = tile.walkable
        self.is_cache_dirty = False

    def is_walkable(self, x: int, y: int, ecs: EntityComponentSystem) -> bool:
        if self.is_cache_dirty:
            self._update_walkable_cache(ecs)
        return self.walkable_tiles.get((x, y), False)

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        grid_position, _ = components
        
        # Движение обрабатывается в InputSystem, здесь только проверка
        pass


class InputSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, PlayerTag]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        grid_position, _ = components
        
        # Система движения для проверки проходимости
        movement_system: GridMovementSystem = ecs.get_system(GridMovementSystem)
        if not movement_system:
            return

        dx, dy = 0, 0
        
        # Обработка событий происходит в цикле игры, здесь только считываем нажатия
        keys = pygame.key.get_pressed()
        
        # Проверяем события однократного нажатия в главном цикле
        # Здесь мы можем реагировать на зажатые клавиши, если нужно, но для пошагового - нет
        # Вместо этого, логику нужно перенести в игровой цикл в main.py
        pass

        

