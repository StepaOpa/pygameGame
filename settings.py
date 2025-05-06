from dataclasses import dataclass
import utils


@dataclass
class Screen:
    WIDTH = 800
    HEIGHT = 600
    BACKGROUND_COLOR = (0, 0, 0)
    DISPLAY_RATIO = 2


@dataclass
class Game:
    TARGET_FPS = 60
    DEBUG = False


@dataclass
class Player:
    SPEED = 3


@dataclass
class Enemy:
    SPEED = 1
    HEALTH = 3
    DETECTION_RANGE = 300


@dataclass
class Map:
    TILES = {
        'floor': ['Map/floor_tile_0.png', 'Map/floor_tile_1.png']
    }

    COLORS = {
        'RED': (255, 0, 0, 255),
        'GREEN': (0, 255, 0, 255),
        'BLUE': (0, 0, 255, 255),
        'WHITE': (255, 255, 255, 255),
        'BLACK': (0, 0, 0, 255),
        'BROWN': (143, 86, 59, 255)
    }
