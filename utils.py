import pygame

BASE_IMG_PATH = "data/images/"


def load_image(path: str) -> pygame.image:
    """
    Load image from data/images
    """
    img = pygame.image.load(BASE_IMG_PATH+path).convert()
    img.set_colorkey((0, 0, 0))
    return img
