import pygame
from pygame.math import Vector2
import utils
import settings


class Entity:
    def __init__(self, position: tuple[int, int], sprite_path: str):
        image = utils.load_image(sprite_path)
        self.position = Vector2(position)
        self.image = image
        self.movement = Vector2(0, 0)
        self.x = position[0]
        self.y = position[1]

    def update(self):

        pass

    def render(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.position)


class Player(Entity):
    def __init__(self, position, sprite_path):
        super().__init__(position, sprite_path)
        self.speed = settings.Player.SPEED

    def update(self):
        self.movement = Vector2(0, 0)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.movement.y -= 1
        if keys[pygame.K_s]:
            self.movement.y += 1
        if keys[pygame.K_a]:
            self. movement.x -= 1
        if keys[pygame.K_d]:
            self. movement.x += 1

        if self.movement.length() > 0:
            self.movement = self.movement.normalize() * self.speed

        self.position += self.movement
