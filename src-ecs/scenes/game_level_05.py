from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel05(GameScene):
    """Пятый уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_05.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="Level 5",
            ground_enemies=2,
            flying_enemies=0,
            wizard_enemies=1,
            health_potions=0,
            bombs=2,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        # После завершения этого уровня переходим на уровень 06
        from .game_level_06 import GameSceneLevel06
        self._set_next_scene(GameSceneLevel06)
