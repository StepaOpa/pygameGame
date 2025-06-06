from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId, System
import random
import pygame
import debug
import settings
from pathfinding import AStar


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
        
        movement_system: GridMovementSystem = ecs.get_system(GridMovementSystem)
        if not movement_system:
            return
            
        events = ecs.get_variable('events')
        if not events:
            return

        # Получаем компонент хода
        turn_component = None
        for _, (turn,) in ecs.get_entities_with_components(TurnComponent):
            turn_component = turn
            break

        if not turn_component or not turn_component.is_player_turn:
            return

        # Получаем позиции всех врагов
        enemy_positions = set()
        for _, (enemy_grid_pos, _) in ecs.get_entities_with_components(GridPosition, EnemyTag):
            enemy_positions.add((enemy_grid_pos.x, enemy_grid_pos.y))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    import sys
                    sys.exit()
                    
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT or event.key == pygame.K_a: dx = -1
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d: dx = 1
                if event.key == pygame.K_UP or event.key == pygame.K_w: dy = -1
                if event.key == pygame.K_DOWN or event.key == pygame.K_s: dy = 1

                if dx != 0 or dy != 0:
                    new_x, new_y = grid_position.x + dx, grid_position.y + dy
                    # Проверяем, что новая позиция проходима и не занята врагом
                    if movement_system.is_walkable(new_x, new_y, ecs) and (new_x, new_y) not in enemy_positions:
                        grid_position.x = new_x
                        grid_position.y = new_y
                        # Увеличиваем счетчик ходов
                        turn_component.turn_count += 1
                        # Отмечаем, что игрок сделал ход
                        turn_component.player_moved = True
                        turn_component.is_player_turn = False


class EnemyPathfindingSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, EnemyTag]
        self.pathfinder = AStar()
        self.current_paths = {}  # словарь для хранения текущих путей врагов
        self.enemies_moved = 0  # счетчик сделавших ход врагов

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        # Получаем компонент хода
        turn_component = None
        for _, (turn,) in ecs.get_entities_with_components(TurnComponent):
            turn_component = turn
            break

        if not turn_component or turn_component.is_player_turn:
            return

        # Проверяем, должны ли враги двигаться в этот ход
        if turn_component.turn_count % 2 != 0:  # Двигаемся только на четных ходах
            turn_component.is_player_turn = True
            turn_component.player_moved = False
            return

        grid_position, _ = components
        
        # Получаем позицию игрока
        player_pos = None
        for _, (player_grid_pos, _) in ecs.get_entities_with_components(GridPosition, PlayerTag):
            player_pos = (player_grid_pos.x, player_grid_pos.y)
            break
            
        if not player_pos:
            return

        # Собираем все проходимые клетки
        walkable_tiles = set()
        for _, (tile_grid_pos, tile) in ecs.get_entities_with_components(GridPosition, TileComponent):
            if tile.walkable:
                walkable_tiles.add((tile_grid_pos.x, tile_grid_pos.y))

        # Получаем позиции всех врагов, кроме текущего
        enemy_positions = set()
        for enemy_id, (enemy_grid_pos, _) in ecs.get_entities_with_components(GridPosition, EnemyTag):
            if enemy_id != entity_id:  # Исключаем текущего врага
                enemy_positions.add((enemy_grid_pos.x, enemy_grid_pos.y))

        # Удаляем из проходимых клеток позиции других врагов
        walkable_tiles = walkable_tiles - enemy_positions

        # Находим путь до игрока
        current_pos = (grid_position.x, grid_position.y)
        path = self.pathfinder.find_path(current_pos, player_pos, walkable_tiles)
        
        # Сохраняем путь для отрисовки в режиме отладки
        self.current_paths[entity_id] = path

        # Если есть путь и он содержит больше одной точки, двигаемся к следующей точке
        if len(path) > 1:
            next_pos = path[1]  # Следующая точка в пути
            # Проверяем, не занята ли следующая позиция другим врагом
            if next_pos not in enemy_positions:
                grid_position.x = next_pos[0]
                grid_position.y = next_pos[1]
                self.enemies_moved += 1

                # Проверяем, все ли враги сделали ход
                total_enemies = 0
                for _ in ecs.get_entities_with_components(EnemyTag):
                    total_enemies += 1

                # Если все враги сделали ход, передаем ход игроку
                if self.enemies_moved >= total_enemies:
                    self.enemies_moved = 0  # сбрасываем счетчик
                    turn_component.is_player_turn = True
                    turn_component.player_moved = False

    def draw_debug(self, ecs: EntityComponentSystem):
        if not debug.IS_DEBUG:
            return

        render_target = ecs.get_variable('render_target')
        if not render_target or not render_target.surface:
            return

        # Отрисовка путей для каждого врага
        for entity_id, path in self.current_paths.items():
            if not path:
                continue

            # Рисуем линии пути
            for i in range(len(path) - 1):
                start_pos = (
                    path[i][0] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2,
                    path[i][1] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
                )
                end_pos = (
                    path[i + 1][0] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2,
                    path[i + 1][1] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
                )
                pygame.draw.line(render_target.surface, pygame.Color('red'), start_pos, end_pos, 2)

            # Рисуем точки пути
            for point in path:
                center_pos = (
                    point[0] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2,
                    point[1] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
                )
                pygame.draw.circle(render_target.surface, pygame.Color('yellow'), center_pos, 3)


        

