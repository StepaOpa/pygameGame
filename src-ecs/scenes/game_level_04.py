from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel04(GameScene):
    """Четвертый уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_04.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="Level 4",
            ground_enemies=3,
            flying_enemies=3,
            wizard_enemies=0,
            health_potions=1,
            bombs=4,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        # После завершения этого уровня переходим на уровень 05
        from .game_level_05 import GameSceneLevel05
        self._set_next_scene(GameSceneLevel05)
