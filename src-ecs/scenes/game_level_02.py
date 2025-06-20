from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel02(GameScene):
    """Второй уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_02.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="Level 2",
            ground_enemies=5,
            flying_enemies=0,
            wizard_enemies=0,
            health_potions=1,
            bombs=3,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        from .game_level_03 import GameSceneLevel03
        self._set_next_scene(GameSceneLevel03)

    def _draw_hints(self, surface: pygame.Surface) -> None:
        hint_font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 9)

        hints = [
            "G - подобрать предмет",
            "B - поставить бомбу",
            "H - выпить лечебное зелье"
        ]

        x_start = surface.get_width() - 150
        y_start = 10
        line_height = 14

        bg_width = 140
        bg_height = len(hints) * line_height + 10
        bg_rect = pygame.Rect(x_start - 5, y_start - 5, bg_width, bg_height)

        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        surface.blit(bg_surface, (x_start - 5, y_start - 5))

        pygame.draw.rect(surface, (100, 150, 100), bg_rect, 1)

        for i, hint in enumerate(hints):
            if i == 0:
                color = (150, 255, 150)
                color = (200, 200, 200)

            text_surf = hint_font.render(hint, True, color)
            surface.blit(text_surf, (x_start, y_start + i * line_height))
