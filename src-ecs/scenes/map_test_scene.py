from .base_scene import *


class MapTestScene(Scene):
    """Сцена для тестирования генератора карт"""

    def __init__(self, manager: SceneManager, app: "GameApp") -> None:  # type: ignore
        super().__init__(manager)
        self.app = app
        self.font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 24)
        self.small_font = pygame.font.SysFont(settings.ScreenSettngs.FONT, 16)

        # Сохраняем оригинальный шаблон
        self.original_template = settings.TileMap.TEMPLATE_PATH

        # Находим все доступные шаблоны карт
        templates_dir = settings.GameSettings.BASE_DIR / \
            "data" / "images" / "Map" / "chunk_templates"
        self.templates = []
        if templates_dir.exists():
            for file in templates_dir.glob("*.png"):
                self.templates.append(str(file))

        # Если нет шаблонов, используем оригинальный
        if not self.templates:
            self.templates = [self.original_template]

        self.current_template_index = 0

        # Находим индекс текущего шаблона
        try:
            self.current_template_index = self.templates.index(
                self.original_template)
        except ValueError:
            self.current_template_index = 0

        # Инициализируем ECS только для отображения карты
        self._init_ecs()
        self._generate_current_map()

    def _init_ecs(self):
        """Инициализирует минимальную ECS для отображения карты"""
        self.ecs = EntityComponentSystem()
        self.assets = AssetManager()
        self.factory = EntityFactory(self.ecs, self.assets, self.app.display)

        # Инициализируем только необходимые компоненты
        self.ecs.init_component(Position)
        self.ecs.init_component(GridPosition)
        self.ecs.init_component(TileComponent)
        self.ecs.init_component(RenderTarget)
        self.ecs.init_component(Render)

        # Добавляем переменную для рендера
        self.ecs.add_variable('render_target', RenderTarget(
            surface=self.app.display, assets=self.assets))

        # Добавляем только систему рендера
        self.ecs.add_system(RenderSystem())

    def _generate_current_map(self):
        """Генерирует карту с текущим шаблоном"""
        # Очищаем старые сущности карты
        entities_to_remove = []
        for entity_id, (tile_comp,) in self.ecs.get_entities_with_components(TileComponent):
            entities_to_remove.append(entity_id)

        for entity_id in entities_to_remove:
            self.ecs.remove_entity(entity_id)

        # Устанавливаем новый шаблон
        settings.TileMap.TEMPLATE_PATH = self.templates[self.current_template_index]

        # Создаём новую карту
        self.factory.create_map()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Восстанавливаем оригинальный шаблон и возвращаемся в меню
                    settings.TileMap.TEMPLATE_PATH = self.original_template
                    from .menu_scene import MenuScene
                    self.manager.change(MenuScene(self.manager, self.app))
                elif event.key == pygame.K_LEFT:
                    # Предыдущий шаблон
                    self.current_template_index = (
                        self.current_template_index - 1) % len(self.templates)
                    self._generate_current_map()
                elif event.key == pygame.K_RIGHT:
                    # Следующий шаблон
                    self.current_template_index = (
                        self.current_template_index + 1) % len(self.templates)
                    self._generate_current_map()
                elif event.key == pygame.K_r:
                    # Регенерировать текущую карту
                    self._generate_current_map()

    def update(self, dt: float) -> None:
        pass  # Тестовая сцена статичная

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(Color('black'))

        # Отрисовываем карту
        render_system: RenderSystem = self.ecs.get_system(RenderSystem)
        render_system.draw_all(self.ecs)

        # Информационная панель
        info_y = 10

        # Название текущего шаблона
        template_name = Path(self.templates[self.current_template_index]).name
        title_surf = self.font.render(
            f"Шаблон: {template_name}", True, (255, 255, 255))
        surface.blit(title_surf, (10, info_y))
        info_y += 30

        # Индекс шаблона
        index_surf = self.small_font.render(
            f"Шаблон {self.current_template_index + 1} из {len(self.templates)}", True, (200, 200, 200))
        surface.blit(index_surf, (10, info_y))
        info_y += 25
