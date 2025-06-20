from abc import ABC, abstractmethod
from typing import Optional
import pygame


class Scene(ABC):
    """Базовый класс для всех сцен."""

    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager

    def enter(self) -> None:
        """Вызывается, когда сцена становится активной."""
        pass

    def exit(self) -> None:
        """Вызывается, когда сцена перестаёт быть активной."""
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Обработка входящих событий."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Обновление состояния сцены (dt — время кадра в секундах)."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовка содержимого сцены на указанный surface."""
        pass


class SceneManager:
    """Управляет текущей сценой и осуществляет переключение между ними."""

    def __init__(self, initial_scene: Scene | None = None) -> None:
        self._current_scene: Optional[Scene] = None
        if initial_scene is not None:
            self.change(initial_scene)

    def change(self, new_scene: Scene) -> None:
        """Деактивирует текущую сцену и активирует новую."""
        if self._current_scene is new_scene:
            return
        if self._current_scene is not None:
            self._current_scene.exit()
        self._current_scene = new_scene
        self._current_scene.enter()

    @property
    def current(self) -> Optional[Scene]:
        return self._current_scene

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self._current_scene is not None:
            self._current_scene.handle_events(events)

    def update(self, dt: float) -> None:
        if self._current_scene is not None:
            self._current_scene.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self._current_scene is not None:
            self._current_scene.draw(surface)
