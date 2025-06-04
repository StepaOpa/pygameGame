from dataclasses import dataclass, field
from pathlib import Path
import pygame
import random
from typing import Dict, List, Tuple
import os
from settings import GameSettings


BASE_DIR = Path(__file__).resolve().parent.parent
BASE_IMG_PATH = BASE_DIR / 'data' / 'images'

TILE_SETS = {
    "floor": ("Map/floor", "floor_tile_"),
    "left_walls": ("Map/walls", "left"),
    "right_walls": ("Map/walls", "right"),
    "top_walls": ("Map/walls", "top"),
    "bottom_walls": ("Map/walls", "bottom"),
    "corners": ("Map/corners", ""),
    "wall_empty": ("", "wall_empty.png")
}
CHUNK_TEMPLATES = {
    "chunk_template_0": ("Map/chunk_templates", "0"),
    "chunk_template_1": ("Map/chunk_templates", "1")
}


@dataclass
class AssetManager:
    """Централизованное управление игровыми ресурсами"""
    base_path: Path = GameSettings.BASE_DIR / 'data' / 'images'
    tile_size: int = 16
    template_size: int = 16

    tiles: Dict[str, List[pygame.Surface]] = field(default_factory=dict)
    chunks: Dict[str, pygame.Surface] = field(default_factory=dict)
    colors: Dict[str, Tuple[int, int, int, int]] = field(default_factory=dict)

    def __post_init__(self):
        self._load_assets()

    def _load_assets(self):
        """Загружает все ресурсы при инициализации"""
        self._load_tiles()
        self._load_colors()

    def _load_tiles(self):
        """Автоматическая загрузка тайлов из папок"""
        for name, (folder, pattern) in TILE_SETS.items():
            self.tiles[name] = self._load_tile_set(folder, pattern)

        for name, (folder, index) in CHUNK_TEMPLATES.items():
            self.chunks[name] = self._load_chunks(index)

    def _load_chunks(self, index: int) -> pygame.Surface:
        path = self.base_path / 'Map/chunk_templates' / \
            'chunk_template_{}.png'.format(index)
        return self._load_image(path)

    def _load_tile_set(self, folder: str, pattern: str) -> List[pygame.Surface]:
        """Загружает набор тайлов из указанной папки"""
        path = self.base_path / folder

        if not path.is_dir() and not pattern.endswith(".png"):
            return []

        if pattern.endswith(".png"):
            file_path = Path(self.base_path) / folder / pattern
            return [self._load_image(file_path)] if file_path.exists() else []

        return [
            self._load_image(f)
            for f in path.glob("*.png")
            if pattern in f.name
        ]

    def _load_image(self, path: Path) -> pygame.Surface:
        """Безопасная загрузка изображения"""
        try:
            img = pygame.image.load(str(path)).convert_alpha()
            # if img.get_size() != (self.tile_size, self.tile_size):
            #     img = pygame.transform.scale(
            #         img, (self.tile_size, self.tile_size))
            #     img.set_colorkey((0, 0, 0))
            return img
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading {path}: {e}")
            return self._create_placeholder()

    def _create_placeholder(self) -> pygame.Surface:
        """Создает тайл-заглушку"""
        surf = pygame.Surface(
            (self.tile_size, self.tile_size), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 128))
        pygame.draw.rect(
            surf, (0, 0, 0), (0, 0, self.tile_size, self.tile_size), 1)
        return surf

    def _load_colors(self):
        """Загружает цветовую палитру"""
        self.colors = {
            "RED": (255, 0, 0, 255),
            "GREEN": (0, 255, 0, 255),
            "BLUE": (0, 0, 255, 255),
            "WHITE": (255, 255, 255, 255),
            "BLACK": (0, 0, 0, 255),
            "BROWN": (143, 86, 59, 255)
        }

    def get_chunk(self, chunk_type: str) -> pygame.Surface:
        """Возвращает чанк указанного типа"""
        return self.chunks.get(chunk_type, [0])

    def get_random_chunk(self, chunk_type: str) -> pygame.Surface:
        """Возвращает случайный чанк указанного типа"""
        return random.choice(self.chunks.get(chunk_type, [self._create_placeholder()]))

    def get_random_tile(self, tile_type: str) -> pygame.Surface:
        """Возвращает случайный тайл указанного типа"""
        return random.choice(self.tiles.get(tile_type, [self._create_placeholder()]))

    def get_tile(self, tile_type: str) -> pygame.Surface:
        """Returns a specific tile of the given type"""
        return next((tile for tile in self.tiles.get(tile_type, []) if tile), self._create_placeholder())

    def get_color(self, color_name: str) -> Tuple[int, int, int, int]:
        """Возвращает цвет по имени"""
        return self.colors.get(color_name, (0, 0, 0, 255))

    def get_sprite(self, sprite_name: str) -> pygame.Surface:
        """Возвращает спрайт по имени data/images... """
        path = BASE_IMG_PATH / sprite_name
        if path.exists():
            return self._load_image(path)
        else:
            print(f"Sprite {sprite_name} not found!")
            return self._create_placeholder()
