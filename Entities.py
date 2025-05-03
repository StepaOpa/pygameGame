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
        self.health = 1

    def update(self):

        pass

    def render(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.position)


class Player(Entity):
    def __init__(self, position: tuple[int, int], sprite_path: str):
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


class Enemy(Entity):
    def __init__(self, position: tuple[int, int], sprite_path: str, player_reference: Player):
        super().__init__(position, sprite_path)
        self.health = settings.Enemy.HEALTH
        self.speed = settings.Enemy.SPEED
        self.player = player_reference
        self.detection_range = settings.Enemy.DETECTION_RANGE

    def update(self):
        direction = Vector2(self.player.position - self.position)
        if direction.length() <= self.detection_range:
            self.movement = direction.normalize()
            self.position += self.movement * self.speed
