from .base_scene import *


class MenuScene(Scene):
    """Простое стартовое меню"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
        self.title_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, 28, bold=True)
        self.menu_font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 18)
        self.options = ["Начать игру", "Тест генератора карт", "Выход"]
        self.selected = 0
        self.title_animation_time = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    try:
                        SoundEngine.get().play('menu_navigate', volume=0.5)
                    except RuntimeError:
                        pass
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    try:
                        SoundEngine.get().play('menu_navigate', volume=0.5)
                    except RuntimeError:
                        pass
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    try:
                        SoundEngine.get().play('menu_select', volume=0.7)
                    except RuntimeError:
                        pass
                    if self.selected == 0:
                        from .tutorial_scene import TutorialScene
                        self.manager.change(
                            TutorialScene(self.manager, self.app))
                    elif self.selected == 1:
                        from .map_test_scene import MapTestScene
                        self.manager.change(
                            MapTestScene(self.manager, self.app))
                    else:
                        self.app.running = False

    def update(self, dt: float) -> None:
        self.title_animation_time += dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((25, 25, 35))

    def draw_hd_ui(self, hd_surface: pygame.Surface) -> None:
        """Отрисовка UI в высоком разрешении для четких шрифтов"""
        import math

        scale_factor = settings.ScreenSettngs.DISPLAY_RATIO

        hd_title_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(28 * scale_factor), bold=True)
        hd_menu_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(18 * scale_factor))
        hd_hint_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(12 * scale_factor))

        hd_surface.fill((25, 25, 35))

        pulse_scale = 0.9 + 0.05 * math.sin(self.title_animation_time * 3.0)

        title_surf = hd_title_font.render(
            "Spooky Dungeon", True, (220, 180, 120))

        scaled_width = int(title_surf.get_width() * pulse_scale)
        scaled_height = int(title_surf.get_height() * pulse_scale)
        scaled_title = pygame.transform.smoothscale(
            title_surf, (scaled_width, scaled_height))

        title_x = (hd_surface.get_width() - scaled_title.get_width()) // 2
        title_y = hd_surface.get_height() // 5 - scaled_title.get_height() // 2
        hd_surface.blit(scaled_title, (title_x, title_y))

        spacing = int(20 * scale_factor)
        total_height = len(
            self.options) * hd_menu_font.get_height() + (len(self.options)-1) * spacing
        start_y = hd_surface.get_height() // 2 - total_height // 2 + \
            int(20 * scale_factor)

        for i, text in enumerate(self.options):
            if i == self.selected:
                color = (255, 200, 100)
                text_surf = hd_menu_font.render(text, True, color)
                text_x = (hd_surface.get_width() - text_surf.get_width()) // 2
                text_y = start_y + i * (hd_menu_font.get_height() + spacing)

                padding = int(8 * scale_factor)
                rect = pygame.Rect(text_x - padding, text_y - int(2 * scale_factor),
                                   text_surf.get_width() + padding * 2,
                                   text_surf.get_height() + int(4 * scale_factor))
                pygame.draw.rect(hd_surface, (60, 60, 80), rect)
                pygame.draw.rect(hd_surface, (255, 200, 100),
                                 rect, int(2 * scale_factor))

                hd_surface.blit(text_surf, (text_x, text_y))
            else:
                color = (180, 180, 190)
                text_surf = hd_menu_font.render(text, True, color)
                text_x = (hd_surface.get_width() - text_surf.get_width()) // 2
                text_y = start_y + i * (hd_menu_font.get_height() + spacing)
                hd_surface.blit(text_surf, (text_x, text_y))

        hint_texts = [
            "W (up) / S (down) - навигация",
            "Enter/Space - выбор"
        ]

        hint_spacing = int(4 * scale_factor)
        total_hint_height = len(
            hint_texts) * hd_hint_font.get_height() + (len(hint_texts) - 1) * hint_spacing
        start_hint_y = hd_surface.get_height() - int(10 * scale_factor) - \
            total_hint_height

        for i, hint_text in enumerate(hint_texts):
            hint_surf = hd_hint_font.render(hint_text, True, (120, 120, 130))
            hint_x = (hd_surface.get_width() - hint_surf.get_width()) // 2
            hint_y = start_hint_y + i * \
                (hd_hint_font.get_height() + hint_spacing)
            hd_surface.blit(hint_surf, (hint_x, hint_y))
