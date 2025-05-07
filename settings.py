from dataclasses import dataclass
import utils


@dataclass
class Screen:
    WIDTH = 1024
    HEIGHT = 1024
    BACKGROUND_COLOR = (0, 0, 0)
    DISPLAY_RATIO = 2


@dataclass
class Map:
    TEMPLATE_SIZE = 16
    TILE_SIZE = 16
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
