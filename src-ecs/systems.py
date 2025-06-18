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

        # Центрируем спрайты в тайле, если размеры отличаются от TILE_SIZE
        render: Render = None  # type: ignore
        try:
            render = ecs.get_component(entity_id, Render)
        except KeyError:
            render = None

        if render and render.sprite:
            sprite_w = int(render.sprite.get_width() * render.scale)
            sprite_h = int(render.sprite.get_height() * render.scale)
            offset_x = (settings.TileMap.TILE_SIZE - sprite_w) // 2
            offset_y = (settings.TileMap.TILE_SIZE - sprite_h) // 2
            position.position.x += offset_x
            position.position.y += offset_y


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
        enemy_positions: dict[tuple[int, int], EntityId] = {}
        for e_id, (enemy_grid_pos, _) in ecs.get_entities_with_components(GridPosition, EnemyTag):
            enemy_positions[(enemy_grid_pos.x, enemy_grid_pos.y)] = e_id

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

                # Поднятие предмета
                if event.key == pygame.K_g:
                    # Ищем предметы в текущей клетке
                    for item_id, (item_comp, _) in ecs.get_entities_with_components(Item, GridPosition):
                        item_grid = ecs.get_component(item_id, GridPosition)
                        if item_grid and item_grid.x == grid_position.x and item_grid.y == grid_position.y:
                            inv = ecs.get_component(entity_id, Inventory)
                            rend = ecs.get_component(item_id, Render)
                            if inv and rend and len(inv.items) < inv.capacity:
                                inv.items.append(InventoryItem(name=item_comp.name, sprite=rend.sprite))
                                ecs.remove_entity(item_id)
                            break
                    continue  # не тратим ход

                # Использование зелья здоровья
                if event.key == pygame.K_h:
                    inv = ecs.get_component(entity_id, Inventory)
                    player_health = ecs.get_component(entity_id, Health)
                    if inv and player_health:
                        for inv_item in inv.items:
                            if inv_item.name == 'Health Potion' and player_health.amount < player_health.max_amount:
                                player_health.amount = min(player_health.max_amount, player_health.amount + 30)
                                inv.items.remove(inv_item)
                                break
                    continue

                # Установка бомбы
                if event.key == pygame.K_b:
                    inv = ecs.get_component(entity_id, Inventory)
                    if inv:
                        # ищем бомбу в инвентаре
                        for inv_item in inv.items:
                            if inv_item.name == 'Bomb':
                                # проверить, свободна ли клетка (нет других бомб)
                                occupied = False
                                for _, (b_grid_pos, __) in ecs.get_entities_with_components(GridPosition, Bomb):
                                    if b_grid_pos.x == grid_position.x and b_grid_pos.y == grid_position.y:
                                        occupied = True
                                        break
                                if occupied:
                                    break

                                # создать бомбу на текущей клетке
                                sprite = inv_item.sprite
                                turn_count = turn_component.turn_count if turn_component else 0
                                new_bomb_id = ecs.create_entity([
                                    Position(position=pygame.Vector2(grid_position.x * settings.TileMap.TILE_SIZE,
                                                                     grid_position.y * settings.TileMap.TILE_SIZE)),
                                    GridPosition(x=grid_position.x, y=grid_position.y),
                                    Render(sprite=sprite, scale=1.0, layer=1),
                                    Bomb()
                                ])
                                inv.items.remove(inv_item)
                                # инициализируем last_turn_processed
                                bomb_comp_created = ecs.get_component(new_bomb_id, Bomb)
                                if bomb_comp_created:
                                    bomb_comp_created.last_turn_processed = turn_count
                                break
                    continue

                if dx != 0 or dy != 0:
                    new_x, new_y = grid_position.x + dx, grid_position.y + dy
                    # --------------------------------------------------
                    # 1) Если в клетке враг — атака
                    # 2) Иначе обычное перемещение
                    # --------------------------------------------------
                    action_performed = False
                    if (new_x, new_y) in enemy_positions:
                        enemy_id = enemy_positions[(new_x, new_y)]
                        # Получаем компоненты
                        player_attack = ecs.get_component(entity_id, Attack)
                        enemy_health = ecs.get_component(enemy_id, Health)
                        if player_attack and enemy_health:
                            enemy_health.apply_damage(player_attack.damage)
                            action_performed = True
                    elif movement_system.is_walkable(new_x, new_y, ecs):
                        grid_position.x = new_x
                        grid_position.y = new_y
                        action_performed = True

                    if action_performed:
                        # Увеличиваем счетчик ходов
                        turn_component.turn_count += 1
                        # Отмечаем, что игрок сделал ход
                        turn_component.player_moved = True

                        # Проверяем, есть ли враги
                        any_enemy = False
                        for _ in ecs.get_entities_with_components(EnemyTag):
                            any_enemy = True
                            break

                        # Если врагов нет, ход остаётся у игрока
                        if any_enemy:
                            turn_component.is_player_turn = False
                        else:
                            turn_component.is_player_turn = True


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

        # Удаляем из проходимых клеток позиций других врагов
        walkable_tiles = walkable_tiles - enemy_positions

        # Находим путь до игрока
        current_pos = (grid_position.x, grid_position.y)
        path = self.pathfinder.find_path(current_pos, player_pos, walkable_tiles)[:-1]
        
        # Сохраняем путь для отрисовки в режиме отладки
        self.current_paths[entity_id] = path

        # Если враг стоит рядом с игроком (длина пути 1) -> атака
        if len(path) == 1:
            # Атакуем игрока
            player_id = None
            for p_id, _ in ecs.get_entities_with_components(PlayerTag):
                player_id = p_id
                break
            if player_id is not None:
                enemy_attack = ecs.get_component(entity_id, Attack)
                player_health = ecs.get_component(player_id, Health)
                if enemy_attack and player_health:
                    player_health.apply_damage(enemy_attack.damage)

            self.enemies_moved += 1

            # Проверяем, все ли враги сделали ход
            total_enemies = 0
            for _ in ecs.get_entities_with_components(EnemyTag):
                total_enemies += 1

            if self.enemies_moved >= total_enemies:
                self.enemies_moved = 0
                turn_component.is_player_turn = True
                turn_component.player_moved = False
            return  # атака завершила ход врага

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
        if len(path) <= 1:
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


# ------------------------------------------------------------------
# Bomb System
# ------------------------------------------------------------------


class BombSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Bomb, GridPosition]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        bomb_comp, grid_pos = components
        # Получаем глобальный счётчик ходов игрока
        turn_component = None
        for _, (turn,) in ecs.get_entities_with_components(TurnComponent):
            turn_component = turn
            break
        if turn_component is None:
            return

        current_turn = turn_component.turn_count
        # Если бомба ещё не инициализирована, установим last_turn_processed
        if bomb_comp.last_turn_processed == -1:
            bomb_comp.last_turn_processed = current_turn
            return  # не уменьшаем в тот же ход установки

        if current_turn != bomb_comp.last_turn_processed:
            bomb_comp.turns_left -= (current_turn - bomb_comp.last_turn_processed)
            bomb_comp.last_turn_processed = current_turn

        if bomb_comp.turns_left > 0:
            return

        # Взрыв: ищем сущности в радиусе
        targets = []
        for target_id, (t_grid_pos, t_health) in ecs.get_entities_with_components(GridPosition, Health):
            dist = max(abs(t_grid_pos.x - grid_pos.x), abs(t_grid_pos.y - grid_pos.y))
            if dist <= bomb_comp.radius:
                targets.append((target_id, t_health))

        for tid, th in targets:
            th.apply_damage(bomb_comp.damage)

        # Создаём сущность взрыва с анимацией
        render_target = ecs.get_variable('render_target')
        assets = render_target.assets if render_target else None
        frames = []
        if assets:
            # Загружаем 3 кадра взрыва
            for i in range(1, 4):
                path = f'Effects/explosion/explosion_{i}.png'
                frames.append(assets.get_sprite(path))
        if not frames and assets:
            # запасной кадр
            frames.append(assets.get_sprite('torch/candlestick_1_1.png'))

        if frames:
            tile_sz = settings.TileMap.TILE_SIZE
            target_size = (tile_sz * 3, tile_sz * 3)
            scaled_frames = [pygame.transform.smoothscale(f, target_size) for f in frames]

            # Верхний левый угол 3x3 области (бомба в центре)
            pos_px = pygame.Vector2((grid_pos.x - 1) * tile_sz, (grid_pos.y - 1) * tile_sz)

            ecs.create_entity([
                Position(position=pos_px),
                Render(sprite=scaled_frames[0], scale=1.0, layer=2),
                Animation(frames=scaled_frames, frame_time=100, loop=False, destroy_on_end=True)
            ])

        # Удаляем бомбу и выходим из функции, чтобы предотвратить повторную обработку
        ecs.remove_entity(entity_id)
        return

    # ----- DEBUG DRAW -------------------------------------------------
    def draw_debug(self, ecs: EntityComponentSystem):
        if not debug.IS_DEBUG:
            return

        render_target = ecs.get_variable('render_target')
        if not render_target or not render_target.surface:
            return

        surf = render_target.surface
        tile_sz = settings.TileMap.TILE_SIZE
        for _, (bomb, grid_pos) in ecs.get_entities_with_components(Bomb, GridPosition):
            radius = bomb.radius
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if max(abs(dx), abs(dy)) <= radius:
                        px = (grid_pos.x + dx) * tile_sz
                        py = (grid_pos.y + dy) * tile_sz
                        rect = pygame.Rect(px, py, tile_sz, tile_sz)
                        pygame.draw.rect(surf, pygame.Color(255, 0, 0, 80), rect, 1)


# ------------------------------------------------------------------
# Animation System
# ------------------------------------------------------------------


class AnimationSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [Animation, Render]

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        anim: Animation
        render: Render
        anim, render = components

        delta_ms = ecs.get_variable('delta_ms') or 16  # по умолчанию ~60 FPS
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
            # Обновляем спрайт
            render.sprite = anim.frames[anim.current_frame]


        

