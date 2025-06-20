from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel03(GameScene):
    """Третий уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_03.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="Level 3",
            ground_enemies=3,
            flying_enemies=1,
            wizard_enemies=0,
            health_potions=0,
            bombs=3,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        # После завершения этого уровня переходим на уровень 04
        from .game_level_04 import GameSceneLevel04
        self._set_next_scene(GameSceneLevel04)
