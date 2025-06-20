from .base_scene import *


class VictoryScene(Scene):
    """Сцена поздравлений при завершении всех уровней"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
        self.font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 48)
        self.medium_font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 32)
        self.small_font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 24)
        self.options = ["Сыграть ещё", "Выход"]
        self.selected = 0
        self.animation_time = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 0:
                        from .game_level_01 import GameSceneLevel01
                        self.manager.change(
                            GameSceneLevel01(self.manager, self.app))
                    else:
                        self.app.running = False

    def update(self, dt: float) -> None:
        self.animation_time += dt

    def draw(self, surface: pygame.Surface) -> None:
        # Градиентный фон
        surface.fill((20, 20, 40))

        import math

        # Анимированный заголовок
        pulse_scale = 0.95 + 0.05 * math.sin(self.animation_time * 2.0)

        # Заголовок "ПОЗДРАВЛЯЕМ!"
        title_surf = self.font.render(
            "ПОЗДРАВЛЯЕМ!", True, (255, 215, 0))  # Золотой цвет
        scaled_width = int(title_surf.get_width() * pulse_scale)
        scaled_height = int(title_surf.get_height() * pulse_scale)
        scaled_title = pygame.transform.smoothscale(
            title_surf, (scaled_width, scaled_height))

        title_x = (surface.get_width() - scaled_title.get_width()) // 2
        title_y = surface.get_height() // 6
        surface.blit(scaled_title, (title_x, title_y))

        # Поздравительный текст
        congrats_texts = [
            "Вы прошли все 10 уровней!",
            "Подземелье очищено от монстров!",
            "Вы — настоящий герой!"
        ]

        text_y = surface.get_height() // 3
        for text in congrats_texts:
            text_surf = self.medium_font.render(text, True, (200, 200, 255))
            text_x = (surface.get_width() - text_surf.get_width()) // 2
            surface.blit(text_surf, (text_x, text_y))
            text_y += 40

        # Кнопки меню
        spacing = 50
        total_height = len(
            self.options) * self.small_font.get_height() + (len(self.options)-1) * spacing
        start_y = surface.get_height() * 2 // 3

        for i, text in enumerate(self.options):
            color = (255, 255, 100) if i == self.selected else (180, 180, 180)
            surf = self.small_font.render(text, True, color)
            x = (surface.get_width() - surf.get_width()) // 2
            y = start_y + i * (self.small_font.get_height() + spacing)
            surface.blit(surf, (x, y))

            # Рамка вокруг выбранного пункта
            if i == self.selected:
                padding = 8
                rect = pygame.Rect(
                    x - padding, y - 2, surf.get_width() + padding * 2, surf.get_height() + 4)
                pygame.draw.rect(surface, (100, 100, 150), rect, 2)
