from scene_manager import SceneManager
from scenes import MenuScene
import settings
import pygame


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('MyGame')
        self._screen = pygame.display.set_mode(
            (settings.ScreenSettngs.WIDTH, settings.ScreenSettngs.HEIGHT))
        self.display = pygame.Surface((self._screen.get_width() // settings.ScreenSettngs.DISPLAY_RATIO,
                                       self._screen.get_height() // settings.ScreenSettngs.DISPLAY_RATIO))

        self.clock = pygame.time.Clock()
        self.running = True

        # Scene manager ---------------------------------------------------
        self.scene_manager = SceneManager()
        # Стартуем с меню
        self.scene_manager.change(MenuScene(self.scene_manager, self))

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(settings.GameSettings.TARGET_FPS)
            dt = dt_ms / 1000.0

            events = pygame.event.get()
            self.scene_manager.handle_events(events)
            self.scene_manager.update(dt)
            
            # Отрисовка на внутреннюю поверхность
            self.scene_manager.draw(self.display)
            # Выводим на экран с масштабированием
            self._screen.blit(pygame.transform.scale(self.display, self._screen.get_size()), (0, 0))
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
