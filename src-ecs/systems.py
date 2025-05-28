from ecs import *
import pygame
from components import *


class InputSystem(System):
    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        for entity in self.ecs.get_entities_with(PlayerController, Physics):
            controller = entity.components[PlayerController]
            physics = entity.components[Physics]

            velocity = [0, 0]
            if keys[pygame.K_a]:
                velocity[0] -= 1
            if keys[pygame.K_d]:
                velocity[0] += 1
            if keys[pygame.K_w]:
                velocity[1] -= 1
            if keys[pygame.K_s]:
                velocity[1] += 1

            physics.velocity = (
                velocity[0] * controller.speed,
                velocity[1] * controller.speed
            )


class PhysicsSystem(System):
    def update(self, delta_time):
        for entity in self.ecs.get_entities_with(Physics, Transform):
            physics = entity.components[Physics]
            transform = entity.components[Transform]
            transform.x += physics.velocity_x * delta_time
            transform.y += physics.velocity_y * delta_time


class RenderSystem(System):
    def update(self, delta_time):
        camera = next((e for e in self.ecs.entities.values()
                      if Camera in e.components), None)
        if not camera:
            return

        camera_comp = camera.components[Camera]
        camera_comp.surface.fill((0, 0, 0))

        for entity in self.ecs.entities.values():
            if Transform in entity.components and Sprite in entity.components:
                transform = entity.components[Transform]
                sprite = entity.components[Sprite]

                if not sprite.rect:
                    sprite.rect = sprite.image.get_rect()

                sprite.rect.center = transform.position
                camera_comp.surface.blit(sprite.image, sprite.rect)

        scaled_surface = pygame.transform.scale(
            camera_comp.surface, camera_comp.display_surface.get_size())
        camera_comp.display_surface.blit(scaled_surface, (0, 0))
        pygame.display.update()
