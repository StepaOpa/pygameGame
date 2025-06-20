from scene_manager import SceneManager
from scenes import MenuScene
import settings
import pygame

from inventory_data import GLOBAL_STORAGE
from sound_engine import init_sound_engine, SoundEngine


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

        self.scene_manager = SceneManager()
        self.scene_manager.change(MenuScene(self.scene_manager, self))

        GLOBAL_STORAGE.inventory.clear()

        se = init_sound_engine(music_volume=0.5)
        se.register('footstep')
        se.register('enemy_die')
        se.register('explosion')
        se.register('menu_navigate')
        se.register('menu_select')
        se.register('teleport')
        se.register('player_die')
        se.register('player_attack')
        se.register('player_hurt')
        se.register('heal_potion')
        
        se.play_music('main_theme.mp3', loop=True)

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(settings.GameSettings.TARGET_FPS)
            dt = dt_ms / 1000.0

            events = pygame.event.get()
            self.scene_manager.handle_events(events)
            self.scene_manager.update(dt)
            
            current_scene = self.scene_manager.current
            if hasattr(current_scene, 'draw_hd_ui'):
                current_scene.draw_hd_ui(self._screen)
            else:
                self.scene_manager.draw(self.display)
                self._screen.blit(pygame.transform.scale(self.display, self._screen.get_size()), (0, 0))
            
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
