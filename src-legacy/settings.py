from dataclasses import dataclass
import utils
import os
from pathlib import Path


@dataclass
class ScreenSettngs:
    WIDTH = 1024
    HEIGHT = 1024
    BACKGROUND_COLOR = (0, 0, 0)
    DISPLAY_RATIO = 2


@dataclass
class Map:
    #     TEMPLATE_SIZE = 16
    #     TILE_SIZE = 16
    #     TILES = {
    #         'floor': [f'Map/floor/floor_tile_{i}.png' for i in range(len(os.listdir('data/images/Map/floor/')))],
    #         'left_walls': [f'Map/walls/{tilename}' for tilename in os.listdir('data/images/Map/walls/') if 'left' in tilename],
    #         'right_walls': [f'Map/walls/{tilename}' for tilename in os.listdir('data/images/Map/walls/') if 'right' in tilename],
    #         'bottom_walls': [f'Map/walls/{tilename}' for tilename in os.listdir('data/images/Map/walls/') if 'bottom' in tilename],
    #         'top_walls': [f'Map/walls/{tilename}' for tilename in os.listdir('data/images/Map/walls/') if 'top' in tilename],
    #         'wall_empty': ['Map/wall_empty.png'],
    #         'wall_corners': [f'Map/corners/{tilename}' for tilename in os.listdir('data/images/Map/corners/')]
    #         # 'walls': [f'Map/walls/wall_tile_{i}.png' for i in range(len(os.listdir('data/images/Map/walls/')) - 4)]
    #     }

    COLORS = {
        'RED': (255, 0, 0, 255),
        'GREEN': (0, 255, 0, 255),  # walls
        'BLUE': (0, 0, 255, 255),
        'WHITE': (255, 255, 255, 255),
        'BLACK': (0, 0, 0, 255),
        'BROWN': (143, 86, 59, 255)  # floor
    }


@dataclass
class GameSettings:
    TARGET_FPS = 60
    DEBUG = False
    BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class PlayerSettngs:
    SPEED = 3


@dataclass
class EnemySettings:
    SPEED = 1
    HEALTH = 3
    DETECTION_RANGE = 300
