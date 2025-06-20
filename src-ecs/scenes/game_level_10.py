from .base_scene import *
from .game_scene import GameScene


class GameSceneLevel10(GameScene):
    """Десятый (финальный) уровень игры"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        self._prev_template = settings.TileMap.TEMPLATE_PATH
        alt_template = str(
            settings.GameSettings.BASE_DIR
            / "data" / "images" / "Map" / "levels" / "level_10.png"
        )
        settings.TileMap.TEMPLATE_PATH = alt_template
        super().__init__(
            manager,
            app,
            level_name="FINAL LEVEL",
            ground_enemies=5,
            flying_enemies=3,
            wizard_enemies=3,
            health_potions=1,
            bombs=4,
        )
        settings.TileMap.TEMPLATE_PATH = self._prev_template

        # Финальный уровень - после него показываем поздравления
        from .victory_scene import VictoryScene
        self._set_next_scene(VictoryScene)
