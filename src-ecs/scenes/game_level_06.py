from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel06(GameScene):
    """Шестой уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_06.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="Level 6",
            ground_enemies=5,
            flying_enemies=0,
            wizard_enemies=1,
            health_potions=1,
            bombs=3,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        # После завершения этого уровня переходим на уровень 07
        from .game_level_07 import GameSceneLevel07
        self._set_next_scene(GameSceneLevel07)
