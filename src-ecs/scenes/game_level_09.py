from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel09(GameScene):
    """Девятый уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_09.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="Level 9",
            ground_enemies=0,
            flying_enemies=0,
            wizard_enemies=2,
            health_potions=0,
            bombs=0,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        # После завершения этого уровня переходим на уровень 10 (финальный)
        from .game_level_10 import GameSceneLevel10
        self._set_next_scene(GameSceneLevel10)
