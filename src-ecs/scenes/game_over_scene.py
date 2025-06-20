from .base_scene import *


class GameOverScene(Scene):
    """Экран окончания игры. Предлагает сыграть заново или выйти."""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
        self.font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 48)
        self.small_font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 32)
        self.options = ["Сыграть ещё", "Выход"]
        self.selected = 0
        self.animation_time = 0.0  # Время для анимации

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    # --- Звук навигации по меню -------------------
                    try:
                        SoundEngine.get().play('menu_navigate', volume=0.5)
                    except RuntimeError:
                        pass
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    # --- Звук навигации по меню -------------------
                    try:
                        SoundEngine.get().play('menu_navigate', volume=0.5)
                    except RuntimeError:
                        pass
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # --- Звук выбора пункта меню ------------------
                    try:
                        SoundEngine.get().play('menu_select', volume=0.7)
                    except RuntimeError:
                        pass
                    if self.selected == 0:
                        from .game_level_01 import GameSceneLevel01
                        self.manager.change(
                            GameSceneLevel01(self.manager, self.app))
                    else:
                        self.app.running = False

    def update(self, dt: float) -> None:
        # Обновляем анимацию
        self.animation_time += dt

    def draw(self, surface: pygame.Surface) -> None:
        # Темно-красный фон для трагичности
        surface.fill((40, 10, 10))

    def draw_hd_ui(self, hd_surface: pygame.Surface) -> None:
        """Отрисовка UI в высоком разрешении для четких шрифтов"""
        import math

        # Коэффициент масштабирования для высокого разрешения
        scale_factor = settings.ScreenSettngs.DISPLAY_RATIO

        # Создаем шрифты в высоком разрешении
        hd_title_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(48 * scale_factor), bold=True)
        hd_menu_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(24 * scale_factor))
        hd_hint_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(12 * scale_factor))

        # Темно-красный градиентный фон
        hd_surface.fill((40, 10, 10))

        # Анимированный заголовок "GAME OVER" с мерцанием ----------------
        # Создаем эффект мерцания
        flicker_intensity = 0.7 + 0.3 * math.sin(self.animation_time * 8.0)
        pulse_scale = 0.7 + 0.05 * math.sin(self.animation_time * 2.0)

        # Цвет с мерцанием
        red_component = int(255 * flicker_intensity)
        title_color = (red_component, 50, 50)

        # Рендерим заголовок в высоком разрешении
        title_surf = hd_title_font.render("GAME OVER", True, title_color)

        # Масштабируем заголовок
        scaled_width = int(title_surf.get_width() * pulse_scale)
        scaled_height = int(title_surf.get_height() * pulse_scale)
        scaled_title = pygame.transform.smoothscale(
            title_surf, (scaled_width, scaled_height))

        # Позиционируем заголовок
        title_x = (hd_surface.get_width() - scaled_title.get_width()) // 2
        title_y = hd_surface.get_height() // 5 - scaled_title.get_height() // 2
        hd_surface.blit(scaled_title, (title_x, title_y))

        # Добавляем тень под заголовком для драматичности
        shadow_offset = int(3 * scale_factor)
        shadow_surf = hd_title_font.render("GAME OVER", True, (20, 5, 5))
        scaled_shadow = pygame.transform.smoothscale(
            shadow_surf, (scaled_width, scaled_height))
        hd_surface.blit(
            scaled_shadow, (title_x + shadow_offset, title_y + shadow_offset))
        hd_surface.blit(scaled_title, (title_x, title_y))

        # Кнопки меню ----------------------------------------------------
        spacing = int(20 * scale_factor)  # масштабированное расстояние
        total_height = len(
            self.options) * hd_menu_font.get_height() + (len(self.options)-1) * spacing
        start_y = hd_surface.get_height() // 2 - total_height // 2 + \
            int(40 * scale_factor)

        for i, text in enumerate(self.options):
            # Цвета для выделения выбранного пункта
            if i == self.selected:
                color = (255, 150, 150)  # Светло-красный для выбранного
                # Добавляем рамку вокруг выбранного пункта
                text_surf = hd_menu_font.render(text, True, color)
                text_x = (hd_surface.get_width() - text_surf.get_width()) // 2
                text_y = start_y + i * (hd_menu_font.get_height() + spacing)

                # Рамка (масштабированная)
                padding = int(8 * scale_factor)
                rect = pygame.Rect(text_x - padding, text_y - int(2 * scale_factor),
                                   text_surf.get_width() + padding * 2,
                                   text_surf.get_height() + int(4 * scale_factor))
                pygame.draw.rect(hd_surface, (80, 30, 30), rect)
                pygame.draw.rect(hd_surface, (255, 100, 100),
                                 rect, int(2 * scale_factor))

                hd_surface.blit(text_surf, (text_x, text_y))
            else:
                # Тусклый красноватый для обычных пунктов
                color = (180, 120, 120)
                text_surf = hd_menu_font.render(text, True, color)
                text_x = (hd_surface.get_width() - text_surf.get_width()) // 2
                text_y = start_y + i * (hd_menu_font.get_height() + spacing)
                hd_surface.blit(text_surf, (text_x, text_y))

        # Добавляем подсказки управления внизу
        hint_texts = [
            "W (up) / S (down) - навигация",
            "Enter/Space - выбор"
        ]

        hint_spacing = int(4 * scale_factor)  # расстояние между строками
        total_hint_height = len(
            hint_texts) * hd_hint_font.get_height() + (len(hint_texts) - 1) * hint_spacing
        start_hint_y = hd_surface.get_height() - int(10 * scale_factor) - \
            total_hint_height

        for i, hint_text in enumerate(hint_texts):
            hint_surf = hd_hint_font.render(hint_text, True, (120, 80, 80))
            hint_x = (hd_surface.get_width() - hint_surf.get_width()) // 2
            hint_y = start_hint_y + i * \
                (hd_hint_font.get_height() + hint_spacing)
            hd_surface.blit(hint_surf, (hint_x, hint_y))
