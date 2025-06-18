import pygame
from pygame import Color

import settings
from assets import AssetManager
from entity_factory import EntityFactory
from entity_component_system import EntityComponentSystem
from components import *
from systems import *
from scene_manager import Scene, SceneManager


class MenuScene(Scene):
    """Простое стартовое меню"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
        self.font = pygame.font.SysFont('arial', 48)
        self.small_font = pygame.font.SysFont('arial', 32)
        self.options = ["Начать игру", "Выход"]
        self.selected = 0

    # ---------------------------------------------------------------------
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 0:
                        self.manager.change(GameScene(self.manager, self.app))
                    else:
                        self.app.running = False

    def update(self, dt: float) -> None:
        pass  # меню статичное

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((30, 30, 30))
        # Заголовок ------------------------------------------------------
        title_surf = self.font.render("Моя Игра", True, (255, 255, 255))
        title_x = (surface.get_width() - title_surf.get_width()) // 2
        title_y = surface.get_height() // 4 - title_surf.get_height() // 2
        surface.blit(title_surf, (title_x, title_y))

        # Кнопки ---------------------------------------------------------
        spacing = 30  # расстояние между опциями
        total_height = len(self.options) * self.small_font.get_height() + (len(self.options)-1) * spacing
        start_y = surface.get_height() // 2 - total_height // 2

        for i, text in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            surf = self.small_font.render(text, True, color)
            x = (surface.get_width() - surf.get_width()) // 2
            y = start_y + i * (self.small_font.get_height() + spacing)
            surface.blit(surf, (x, y))


class GameScene(Scene):
    """Основная игровая сцена (пошаговая игра на ECS)"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
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
        self.ecs.init_component(Collider)
        self.ecs.init_component(Velocity)
        self.ecs.init_component(DamageOnContact)
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

        # Переменные
        self.ecs.add_variable('render_target', RenderTarget(surface=self.app.display, assets=self.assets))

        # Системы
        self.ecs.add_system(InputSystem())
        self.ecs.add_system(GridMovementSystem())
        self.ecs.add_system(PositionSyncSystem())
        self.ecs.add_system(DamageOnContactSystem())
        self.ecs.add_system(DeathSystem())
        self.ecs.add_system(RenderSystem())
        self.ecs.add_system(BombSystem())
        self.ecs.add_system(AnimationSystem())
        self.enemy_pathfinding_system = EnemyPathfindingSystem()
        self.ecs.add_system(self.enemy_pathfinding_system)

        # Карта и сущности
        self.factory.create_map()
        self.factory.create_player(2,2)
        self.factory.create_enemy()
        self.factory.create_enemy()
        self.factory.create_enemy()
        # Сущность для ходов
        self.ecs.create_entity([TurnComponent()])

        # Положим зелье на карту для теста
        self.factory.create_health_potion(4, 4)
        self.factory.create_bomb_pickup()
        self.factory.create_bomb_pickup()
    # ------------------------------------------------------------------
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        # Передаём события в ECS
        self.ecs.add_variable('events', events)
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Возврат в меню
                self.manager.change(MenuScene(self.manager, self.app))

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
        # Проверяем, жив ли игрок
        player_alive = False
        for _ in self.ecs.get_entity_ids_with_components(PlayerTag):
            player_alive = True
            break
        if not player_alive:
            # Переходим на GameOver сцену
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

        # ---------------- UI: здоровье игрока -------------------------
        player_health = None
        for _, (health, _) in self.ecs.get_entities_with_components(Health, PlayerTag):
            player_health = health
            break
        if player_health is not None:
            font = pygame.font.SysFont('arial', 16)
            text_surf = font.render(f"HP: {player_health.amount}/{player_health.max_amount}", True, (255, 255, 255))
            surface.blit(text_surf, (5, 5))

        # ---------------- HP врагов ------------------------------------
        for _, (enemy_pos, enemy_health, _) in self.ecs.get_entities_with_components(Position, Health, EnemyTag):
            # Полоска здоровья
            max_bar_width = settings.TileMap.TILE_SIZE
            bar_height = 4
            bar_x = enemy_pos.position.x
            bar_y = enemy_pos.position.y - bar_height - 2  # чуть выше спрайта

            # Красный фон
            pygame.draw.rect(surface, (150, 0, 0), (bar_x, bar_y, max_bar_width, bar_height))
            # Зелёная заполненная часть
            hp_ratio = enemy_health.amount / enemy_health.max_amount if enemy_health.max_amount else 0
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, int(max_bar_width * hp_ratio), bar_height))

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
                font_inv = pygame.font.SysFont('arial', 14)
                surf_inv = font_inv.render("Инвентарь пуст", True, (200, 200, 200))
                surface.blit(surf_inv, (x_offset, y_offset))
            else:
                for idx, inv_item in enumerate(inv_comp.items):
                    icon = pygame.transform.smoothscale(inv_item.sprite, (icon_size, icon_size))
                    surface.blit(icon, (x_offset + idx * (icon_size + padding), y_offset))


# ---------------------------------------------------------------------
# GameOver Scene
# ---------------------------------------------------------------------


class GameOverScene(Scene):
    """Экран окончания игры. Предлагает сыграть заново или выйти."""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
        self.font = pygame.font.SysFont('arial', 48)
        self.small_font = pygame.font.SysFont('arial', 32)
        self.options = ["Сыграть ещё", "Выход"]
        self.selected = 0

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 0:
                        self.manager.change(GameScene(self.manager, self.app))
                    else:
                        self.app.running = False

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        title_surf = self.font.render("GAME OVER", True, (255, 0, 0))
        title_x = (surface.get_width() - title_surf.get_width()) // 2
        title_y = surface.get_height() // 4 - title_surf.get_height() // 2
        surface.blit(title_surf, (title_x, title_y))

        spacing = 50
        total_height = len(self.options) * self.small_font.get_height() + (len(self.options)-1) * spacing
        start_y = surface.get_height() // 2 - total_height // 2

        for i, text in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            surf = self.small_font.render(text, True, color)
            x = (surface.get_width() - surf.get_width()) // 2
            y = start_y + i * (self.small_font.get_height() + spacing)
            surface.blit(surf, (x, y)) 