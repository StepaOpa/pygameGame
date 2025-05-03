import pygame
from pygame.math import Vector2
import utils
import settings


class Entity:
    def __init__(self, position: tuple[int, int], sprite_path: str):
        self.position = Vector2(position)
        self.image = utils.load_image(sprite_path)
        self.movement = Vector2(0, 0)
        self.rect = self.image.get_rect()
        self.health = 1

    def update(self):
        pass

    def render(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.position)


class PhysicsEntity(Entity):
    def __init__(self, position: tuple[int, int], sprite_path: str):
        super().__init__(position, sprite_path)
        self.collider = self.rect.copy()
        self.collider_offset = Vector2(0, 0)
        self.collision_type = 'solid'

    def render(self, screen):
        super().render(screen)
        if settings.Game.DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), self.collider, 1)

    @staticmethod
    def check_collision(entity1: 'PhysicsEntity', entity2: 'PhysicsEntity') -> bool:
        return entity1.collider.colliderect(entity2.collider)

    def update_collider(self):
        self.collider.x, self.collider.y = self.position.x, self.position.y

    def update(self, entities: list['PhysicsEntity']):
        self.update_collider()

        if self.collision_type == 'solid':
            for entity in entities:
                if entity != self and self.check_collision(self, entity):
                    self.resolve_collision(entity)

    def resolve_collision(self, other: 'PhysicsEntity'):
        overlap_x = min(self.collider.right - other.collider.left,
                        other.collider.right - self.collider.left)
        overlap_y = min(self.collider.bottom - other.collider.top,
                        other.collider.bottom - self.collider.top)

        if overlap_x < overlap_y:
            if self.movement.x > 0:
                self.position.x -= overlap_x
            else:
                self.position.x += overlap_x
        else:
            if self.movement.y > 0:
                self.position.y -= overlap_y
            else:
                self.position.y += overlap_y

        self.update_collider()


class Player(PhysicsEntity):
    def __init__(self, position: tuple[int, int], sprite_path: str):
        super().__init__(position, sprite_path)
        self.speed = settings.Player.SPEED

    def update(self, delta_time: float, entities: list['PhysicsEntity']):
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
            self.movement = self.movement.normalize() * self.speed * delta_time

        self.position += self.movement
        super().update(entities)


class Enemy(PhysicsEntity):
    def __init__(self, position: tuple[int, int], sprite_path: str, player_reference: Player):
        super().__init__(position, sprite_path)
        self.health = settings.Enemy.HEALTH
        self.speed = settings.Enemy.SPEED
        self.player = player_reference
        self.detection_range = settings.Enemy.DETECTION_RANGE

    def update(self, delta_time: float, entities: list['PhysicsEntity']):
        direction = Vector2(self.player.position - self.position)
        distance = direction.length()
        if distance <= self.detection_range and distance > 0:
            self.movement = direction.normalize()
            self.position += self.movement * self.speed * delta_time
        super().update(entities)
