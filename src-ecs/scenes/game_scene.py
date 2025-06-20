from .base_scene import *


class GameScene(Scene):
    """Основная игровая сцена (пошаговая игра на ECS)

    Параметры:
        level_name – название уровня
        ground_enemies – количество обычных врагов
        flying_enemies – количество летающих врагов
        wizard_enemies – количество врагов-магов
        health_potions – количество зелий здоровья на уровне
        bombs – количество бомб на уровне
    """

    def __init__(
        self,
        manager: SceneManager,
        app: "GameApp",
        *,
        level_name: str = "Level 1",
        ground_enemies: int = 3,
        flying_enemies: int = 1,
        wizard_enemies: int = 0,
        health_potions: int = 1,
        bombs: int = 2,
    ) -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
        self.level_name = level_name
        # -----------------------------------------------------------------
        # Инициализируем ECS и всё, что раньше было в Game.__init__.
        # -----------------------------------------------------------------
        self.ecs = EntityComponentSystem()
        self.assets = AssetManager()
        self.factory = EntityFactory(self.ecs, self.assets, self.app.display)

        # Компоненты
        self.ecs.init_component(Position)
        self.ecs.init_component(GridPosition)
        self.ecs.init_component(TileComponent)
        self.ecs.init_component(Velocity)
        self.ecs.init_component(Health)
        self.ecs.init_component(Attack)
        self.ecs.init_component(RenderTarget)
        self.ecs.init_component(Render)
        self.ecs.init_component(PlayerTag)
        self.ecs.init_component(EnemyTag)
        self.ecs.init_component(TurnComponent)
        self.ecs.init_component(Inventory)
        self.ecs.init_component(Item)
        self.ecs.init_component(HealEffect)
        self.ecs.init_component(Bomb)
        self.ecs.init_component(Animation)
        self.ecs.init_component(FlyingEnemyTag)
        self.ecs.init_component(WizardTag)
        self.ecs.init_component(Fireball)
        self.ecs.init_component(WizardState)
        self.ecs.init_component(Hitbox)
        self.ecs.init_component(Explosion)

        # Переменные
        self.ecs.add_variable('render_target', RenderTarget(
            surface=self.app.display, assets=self.assets))

        # Системы
        self.ecs.add_system(InputSystem())
        self.ecs.add_system(GridMovementSystem())
        self.ecs.add_system(PositionSyncSystem())
        self.ecs.add_system(DeathSystem())
        self.ecs.add_system(RenderSystem())
        self.ecs.add_system(BombSystem())
        self.ecs.add_system(AnimationSystem())
        self.ecs.add_system(FireballSystem())
        self.hitbox_debug_system = HitboxDebugSystem()
        self.ecs.add_system(self.hitbox_debug_system)
        self.enemy_pathfinding_system = EnemyPathfindingSystem()
        self.ecs.add_system(self.enemy_pathfinding_system)
        self.ecs.add_system(ExplosionSystem())
        # Система переноса инвентаря между уровнями
        self.ecs.add_system(InventoryPersistenceSystem())

        # Карта и сущности
        spawn_coords, self.exit_coords = self.factory.create_map()
        if spawn_coords is None:
            spawn_coords = (2, 2)  # Fallback, если пиксель спавна не найден
        self.factory.create_player(*spawn_coords)
        # -------------------- ВРАГИ -----------------------------------
        for _ in range(max(0, ground_enemies)):
            self.factory.create_enemy()
        for _ in range(max(0, flying_enemies)):
            self.factory.create_flying_enemy()
        for _ in range(max(0, wizard_enemies)):
            self.factory.create_wizard_enemy()
        # Сущность для ходов
        self.ecs.create_entity([TurnComponent()])

        # Создаём зелья и бомбы в случайных местах
        self._place_items_randomly(health_potions, bombs)

        self.exit_tile_spawned = False
        # По умолчанию класс следующей сцены — None, переопределяется ниже
        self.next_scene_cls = None  # type: ignore
        # По умолчанию следующий уровень — GameSceneLevel01
        # (класс определяется далее в файле, поэтому ссылка допустима)
        try:
            from .game_level_01 import GameSceneLevel01
            self._set_next_scene(GameSceneLevel01)  # type: ignore  # noqa: F821
        except ImportError:
            # Класс ещё не определён в момент импорта — оставим None,
            # подкласс или внешний код должен установить вручную.
            pass

    # ------------------------------------------------------------------
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        # Передаём события в ECS
        self.ecs.add_variable('events', events)
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Возврат в меню
                from .menu_scene import MenuScene
                self.manager.change(MenuScene(self.manager, self.app))
            # --- Переход на второй уровень ---------------------------------
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                # Загружаем вторую сцену-уровень
                from .game_level_01 import GameSceneLevel01
                self.manager.change(GameSceneLevel01(self.manager, self.app))

    def update(self, dt: float) -> None:
        # передаём dt (мс) системам
        self.ecs.add_variable('delta_ms', int(dt * 1000))
        self.ecs.update()

        # Если врагов нет, гарантируем ход игрока
        enemy_exists = False
        for _ in self.ecs.get_entities_with_components(EnemyTag):
            enemy_exists = True
            break
        if not enemy_exists:
            for _, (turn_comp,) in self.ecs.get_entities_with_components(TurnComponent):
                turn_comp.is_player_turn = True
                turn_comp.player_moved = False

            # Если все враги повержены и выход ещё не создан — создаём
            if not self.exit_tile_spawned and self.exit_coords is not None:
                self.factory.create_exit_tile(*self.exit_coords)
                # Визуальный эффект взрыва как у бомбы
                self.factory.create_explosion_effect(*self.exit_coords)
                # --- Звук телепорта при появлении лестницы ----------------
                try:
                    SoundEngine.get().play('teleport_summon', volume=0.8)
                except RuntimeError:
                    pass
                self.exit_tile_spawned = True

        # Если выход создан, проверяем, стоит ли игрок на клетке выхода
        if self.exit_tile_spawned and self.exit_coords is not None:
            # Получаем позицию игрока на сетке
            player_grid = None
            for _, (grid_pos, _) in self.ecs.get_entities_with_components(GridPosition, PlayerTag):
                player_grid = (grid_pos.x, grid_pos.y)
                break
            if player_grid == self.exit_coords and self.next_scene_cls is not None:
                # --- Звук телепорта при переходе на следующий уровень -----
                try:
                    SoundEngine.get().play('teleport', volume=0.7)
                except RuntimeError:
                    pass
                # Переходим на следующий уровень
                self.manager.change(
                    self.next_scene_cls(self.manager, self.app))

        # Проверяем, жив ли игрок (если умер — GameOver)
        player_alive = False
        for _ in self.ecs.get_entity_ids_with_components(PlayerTag):
            player_alive = True
            break
        if not player_alive:
            from .game_over_scene import GameOverScene
            self.manager.change(GameOverScene(self.manager, self.app))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(Color('black'))
        render_system: RenderSystem = self.ecs.get_system(RenderSystem)
        render_system.draw_all(self.ecs)
        self.enemy_pathfinding_system.draw_debug(self.ecs)

        # подсветка зоны взрыва
        bomb_sys = self.ecs.get_system(BombSystem)
        if bomb_sys:
            bomb_sys.draw_debug(self.ecs)

        # отладочная отрисовка хитбоксов
        self.hitbox_debug_system.draw_debug(self.ecs)

        # ---------------- UI: здоровье игрока -------------------------
        player_health = None
        for _, (health, _) in self.ecs.get_entities_with_components(Health, PlayerTag):
            player_health = health
            break
        if player_health is not None:
            font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 12)
            text_surf = font.render(
                f"HP: {player_health.amount}/{player_health.max_amount}", True, (255, 255, 255))
            surface.blit(text_surf, (5, 5))

        # ---------------- UI: текущий уровень -------------------------
        font_level = pygame.font.SysFont(settings.ScreenSettngs.FONT, 12)
        level_text = font_level.render(self.level_name, True, (255, 255, 255))
        level_rect = level_text.get_rect()
        level_rect.topright = (surface.get_width() - 5, 5)
        surface.blit(level_text, level_rect)

        # ---------------- HP врагов ------------------------------------
        for _, (enemy_pos, enemy_health, _) in self.ecs.get_entities_with_components(Position, Health, EnemyTag):
            # Полоска здоровья
            max_bar_width = settings.TileMap.TILE_SIZE
            bar_height = 4
            bar_x = enemy_pos.position.x
            bar_y = enemy_pos.position.y - bar_height - 2  # чуть выше спрайта

            # Красный фон
            pygame.draw.rect(surface, (150, 0, 0),
                             (bar_x, bar_y, max_bar_width, bar_height))
            # Зелёная заполненная часть
            hp_ratio = enemy_health.amount / \
                enemy_health.max_amount if enemy_health.max_amount else 0
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, int(
                max_bar_width * hp_ratio), bar_height))

        # ---------------- Инвентарь ------------------------------------
        inv_comp = None
        for _, (inv, _) in self.ecs.get_entities_with_components(Inventory, PlayerTag):
            inv_comp = inv
            break
        if inv_comp:
            padding = 4
            icon_size = 16
            x_offset = 5
            y_offset = surface.get_height() - icon_size - 5
            if not inv_comp.items:
                font_inv = pygame.font.SysFont(settings.ScreenSettngs.FONT, 14)
                surf_inv = font_inv.render(
                    "Инвентарь пуст", True, (200, 200, 200))
                surface.blit(surf_inv, (x_offset, y_offset))
            else:
                for idx, inv_item in enumerate(inv_comp.items):
                    icon = pygame.transform.smoothscale(
                        inv_item.sprite, (icon_size, icon_size))
                    surface.blit(
                        icon, (x_offset + idx * (icon_size + padding), y_offset))

        # ---------------- Подсказки управления ------------------------
        self._draw_hints(surface)

    # ------------------------------------------------------------------
    def _draw_hints(self, surface: pygame.Surface) -> None:
        """Отрисовывает подсказки по управлению в правом верхнем углу.
        Переопределяется в подклассах для разных уровней."""
        pass  # По умолчанию подсказки не показываются

    def _place_items_randomly(self, health_potions: int, bombs: int) -> None:
        """Размещает предметы в случайных свободных местах на карте"""
        import random

        # Находим все свободные клетки (пол) на карте
        free_positions = []
        for entity_id, (grid_pos, tile_comp) in self.ecs.get_entities_with_components(GridPosition, TileComponent):
            if tile_comp.tile_type == "floor":
                pos = (grid_pos.x, grid_pos.y)
                # Проверяем, что на этой позиции нет игрока или врагов
                if not self._is_position_occupied(pos):
                    free_positions.append(pos)

        # Перемешиваем позиции для случайного размещения
        random.shuffle(free_positions)

        total_items = health_potions + bombs
        if len(free_positions) < total_items:
            print(
                f"Предупреждение: недостаточно свободных мест для размещения всех предметов")
            total_items = len(free_positions)

        # Размещаем зелья
        potions_placed = min(health_potions, len(free_positions))
        for i in range(potions_placed):
            x, y = free_positions[i]
            self.factory.create_health_potion(x, y)

        # Размещаем бомбы
        bombs_placed = min(bombs, len(free_positions) - potions_placed)
        for i in range(bombs_placed):
            x, y = free_positions[potions_placed + i]
            self.factory.create_bomb_pickup(x, y)

    def _is_position_occupied(self, pos: tuple[int, int]) -> bool:
        """Проверяет, занята ли позиция игроком или врагами"""
        x, y = pos

        # Проверяем игрока
        for _, (grid_pos, _) in self.ecs.get_entities_with_components(GridPosition, PlayerTag):
            if grid_pos.x == x and grid_pos.y == y:
                return True

        # Проверяем врагов
        for _, (grid_pos, _) in self.ecs.get_entities_with_components(GridPosition, EnemyTag):
            if grid_pos.x == x and grid_pos.y == y:
                return True

        return False

    # ------------------------------------------------------------------
    def _set_next_scene(self, scene_cls):
        """Утилита для установки следующей сцены, вызывается подклассами."""
        self.next_scene_cls = scene_cls
