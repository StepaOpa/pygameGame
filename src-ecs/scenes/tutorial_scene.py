from .base_scene import *


class TutorialScene(Scene):
    """Сцена с обучением и инструкциями по управлению"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app

        # Информация об управлении
        self.tutorial_sections = [
            {
                "title": "Движение",
                "controls": [
                    "WASD или стрелки - перемещение",
                    "Игра пошаговая - каждое нажатие = один ход"
                ]
            },
            {
                "title": "Бой",
                "controls": [
                    "Подойдите к врагу чтобы атаковать",
                    "У врагов есть полоски здоровья"
                ]
            },
            {
                "title": "Предметы",
                "controls": [
                    "G - поднять предмет с пола",
                    "H - использовать зелье лечения",
                    "B - поставить бомбу (радиус взрыва 1 клетка)"
                ]
            },
            {
                "title": "Цель",
                "controls": [
                    "Убейте всех врагов на уровне",
                    "Лестница появится после победы",
                    "Встаньте на лестницу для перехода дальше"
                ]
            }
        ]

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Возврат в меню
                    from .menu_scene import MenuScene
                    self.manager.change(MenuScene(self.manager, self.app))
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # --- Звук выбора ------------------
                    try:
                        SoundEngine.get().play('menu_select', volume=0.7)
                    except RuntimeError:
                        pass
                    # Переход к первому уровню
                    from .game_level_01 import GameSceneLevel01
                    self.manager.change(
                        GameSceneLevel01(self.manager, self.app))

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        # В обычном разрешении просто заливаем фон
        surface.fill((25, 25, 35))

    def draw_hd_ui(self, hd_surface: pygame.Surface) -> None:
        """Отрисовка обучения в высоком разрешении для четких шрифтов"""

        # Коэффициент масштабирования для высокого разрешения
        scale_factor = settings.ScreenSettngs.DISPLAY_RATIO

        # Создаем шрифты в высоком разрешении (уменьшены в 2 раза)
        hd_title_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(9 * scale_factor), bold=True)
        hd_section_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(7 * scale_factor), bold=True)
        hd_text_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(9 * scale_factor))
        hd_hint_font = pygame.font.SysFont(
            settings.ScreenSettngs.FONT, int(7 * scale_factor))

        # Темно-серый фон
        hd_surface.fill((25, 25, 35))

        # Заголовок в левом верхнем углу
        title_surf = hd_title_font.render("Как играть", True, (220, 180, 120))
        title_x = int(10 * scale_factor)
        title_y = int(10 * scale_factor)
        hd_surface.blit(title_surf, (title_x, title_y))

        # Отрисовка секций с инструкциями
        current_y = title_y + title_surf.get_height() + int(10 * scale_factor)
        section_spacing = int(8 * scale_factor)
        line_spacing = int(-1 * scale_factor)

        for section in self.tutorial_sections:
            # Заголовок секции
            section_surf = hd_section_font.render(
                section["title"], True, (255, 200, 100))
            section_x = int(10 * scale_factor)
            hd_surface.blit(section_surf, (section_x, current_y))
            current_y += section_surf.get_height() + int(2 * scale_factor)

            # Пункты управления
            for control in section["controls"]:
                control_surf = hd_text_font.render(
                    f"  • {control}", True, (180, 180, 190))
                control_x = int(20 * scale_factor)
                hd_surface.blit(control_surf, (control_x, current_y))
                current_y += control_surf.get_height() + line_spacing

            current_y += section_spacing

        # Подсказки управления внизу
        hint_texts = [
            "Enter/Space - начать игру",
            "Escape - вернуться в меню"
        ]

        hint_spacing = int(4 * scale_factor)
        total_hint_height = len(
            hint_texts) * hd_hint_font.get_height() + (len(hint_texts) - 1) * hint_spacing
        start_hint_y = hd_surface.get_height() - int(20 * scale_factor) - \
            total_hint_height

        for i, hint_text in enumerate(hint_texts):
            hint_surf = hd_hint_font.render(hint_text, True, (120, 120, 130))
            hint_x = (hd_surface.get_width() - hint_surf.get_width()) // 2
            hint_y = start_hint_y + i * \
                (hd_hint_font.get_height() + hint_spacing)
            hd_surface.blit(hint_surf, (hint_x, hint_y))
