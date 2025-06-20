from inventory_data import GLOBAL_STORAGE, ITEM_SPRITE_MAP
from dataclasses import dataclass, field
import os
from pathlib import Path


@dataclass
class ScreenSettngs:
    DISPLAY_RATIO = 2
    WIDTH = 1024/DISPLAY_RATIO
    HEIGHT = 1024/DISPLAY_RATIO
    BACKGROUND_COLOR = (0, 0, 0)
    FONT = 'Verdana'


@dataclass
class GameSettings:
    TARGET_FPS = 60
    DEBUG = False
    BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class TileMap:
    MAP_WIDTH = 16
    MAP_HEIGHT = 16
    TILE_SIZE = 16
    TEMPLATE_PATH = str(GameSettings.BASE_DIR / 'data' / 'images' /
                        'Map' / 'chunk_templates' / 'chunck_template_checker_pro.png')

    FLOOR_TILES = [f'Map/floor/floor_tile_{i}.png' for i in range(12)]

    TILE_VARIANTS = {
        'top_left_corner': 'Map/corners/wall_tile_corner_left_down_outer.png',
        'top_right_corner': 'Map/corners/wall_tile_corner_right_down_outer.png',
        'bottom_left_corner': 'Map/corners/wall_tile_corner_left_down_inner.png',
        'bottom_right_corner': 'Map/corners/wall_tile_corner_right_down_inner.png',
        'top': 'Map/walls/wall_tile_top_0.png',
        'bottom': 'Map/walls/wall_tile_bottom_0.png',
        'left': 'Map/walls/wall_tile_left_0.png',
        'right': 'Map/walls/wall_tile_right_0.png',
        'floor': 'Map/floor/floor_tile_0.png',
        'empty': 'Map/wall_empty.png',
        'stairs': 'Map/ladder.png'
    }

    COLORS = {
        'empty': (0, 0, 0, 0),
        'wall': (0, 255, 0, 255),
        'floor': (143, 86, 59, 255),
        'spawn': (255, 255, 0, 255),
        'exit': (0, 255, 255, 255),
        'entry': (255, 0, 0, 255)
    }


@dataclass
class PlayerSettings:
    SPEED = 3


@dataclass
class EnemySettings:
    SPEED = 1
    HEALTH = 3
    DETECTION_RANGE = 300
