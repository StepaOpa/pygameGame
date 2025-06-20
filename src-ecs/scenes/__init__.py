"""
Модуль сцен игры.

Содержит все игровые сцены:
- MenuScene - главное меню
- TutorialScene - обучение и инструкции
- MapTestScene - тестирование генератора карт
- GameScene - базовая игровая сцена
- GameOverScene - экран окончания игры
- GameSceneLevel01-10 - уровни игры
"""

from .menu_scene import MenuScene
from .tutorial_scene import TutorialScene
from .map_test_scene import MapTestScene
from .game_scene import GameScene
from .game_over_scene import GameOverScene
from .game_level_01 import GameSceneLevel01
from .game_level_02 import GameSceneLevel02
from .game_level_03 import GameSceneLevel03
from .game_level_04 import GameSceneLevel04
from .game_level_05 import GameSceneLevel05
from .game_level_06 import GameSceneLevel06
from .game_level_07 import GameSceneLevel07
from .game_level_08 import GameSceneLevel08
from .game_level_09 import GameSceneLevel09
from .game_level_10 import GameSceneLevel10
from .victory_scene import VictoryScene

__all__ = [
    'MenuScene',
    'TutorialScene',
    'MapTestScene',
    'GameScene',
    'GameOverScene',
    'GameSceneLevel01',
    'GameSceneLevel02',
    'GameSceneLevel03',
    'GameSceneLevel04',
    'GameSceneLevel05',
    'GameSceneLevel06',
    'GameSceneLevel07',
    'GameSceneLevel08',
    'GameSceneLevel09',
    'GameSceneLevel10',
    'VictoryScene',
]
