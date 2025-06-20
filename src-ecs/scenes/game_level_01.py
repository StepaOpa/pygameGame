from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel01(GameScene):
    """Первый уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_01.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="Level 1",
            ground_enemies=2,
            flying_enemies=0,
            wizard_enemies=0,
            health_potions=0,
            bombs=0,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        # После завершения этого уровня переходим на уровень 02
        from .game_level_02 import GameSceneLevel02
        self._set_next_scene(GameSceneLevel02)

    def _draw_hints(self, surface: pygame.Surface) -> None:
        """Отрисовывает подсказки по управлению для первого уровня"""
        hint_font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 11)

        # Подсказки по управлению
        hints = [
            "Управление:",
            "WASD - движение",
            "Esc - выход"
        ]

        # Позиция в правом верхнем углу
        x_start = surface.get_width() - 150
        y_start = 10
        line_height = 14

        # Фон для подсказок с легкой анимацией
        bg_width = 140
        bg_height = len(hints) * line_height + 10
        bg_rect = pygame.Rect(x_start - 5, y_start - 5, bg_width, bg_height)

        # Создаем полупрозрачную поверхность для фона
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        surface.blit(bg_surface, (x_start - 5, y_start - 5))

        # Рамка
        pygame.draw.rect(surface, (150, 150, 100), bg_rect, 1)

        # Отрисовка текста подсказок
        for i, hint in enumerate(hints):
            if i == 0:  # Заголовок
                color = (255, 255, 150)
            else:
                color = (200, 200, 200)

            text_surf = hint_font.render(hint, True, color)
            surface.blit(text_surf, (x_start, y_start + i * line_height))
