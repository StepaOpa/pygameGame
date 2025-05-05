from dataclasses import dataclass


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
