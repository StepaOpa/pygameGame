import pygame
import random
import settings
from assets import AssetManager
import debug
from components import TileComponent, GridPosition, Render
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity_factory import EntityFactory

def get_tile_type_by_color(color):
    """Определяет тип тайла по его цвету"""
    for tile_type, tile_color in settings.TileMap.COLORS.items():
        if color == tile_color:
            return tile_type
    return 'empty'

def get_tile_variant(x, y, pixel_array, width, height):
    """Определяет вариант тайла на основе его соседей"""
    def get_neighbor_type(nx, ny):
        """Возвращает тип соседней клетки (wall, floor или empty)"""
        if 0 <= nx < width and 0 <= ny < height:
            pixel_value = pixel_array[nx, ny]
            # Преобразуем значение пикселя в RGBA
            color = pygame.Color(*pixel_array.surface.unmap_rgb(pixel_value))
            return get_tile_type_by_color((color.r, color.g, color.b, color.a))
        return 'empty'

    # Проверяем типы соседних клеток
    up = get_neighbor_type(x, y-1)
    down = get_neighbor_type(x, y+1)
    left = get_neighbor_type(x-1, y)
    right = get_neighbor_type(x+1, y)

    up_left = get_neighbor_type(x-1, y-1)
    up_right = get_neighbor_type(x+1, y-1)
    down_left = get_neighbor_type(x-1, y+1)
    down_right = get_neighbor_type(x+1, y+1)
    
    if debug.IS_DEBUG:
        print(f"Позиция ({x}, {y})")
        print(f"Соседи: верх={up}, низ={down}, лево={left}, право={right}")
    def wall_checks():
        if left in ['empty', 'wall']  and right == 'floor':
            return 'left'
        if right in ['empty', 'wall'] and left == 'floor': 
            return 'right'
        if up in ['floor', 'empty', 'wall'] and down == 'floor':
            return 'top'
        if down in ['empty', 'wall'] and up == 'floor':  
            return 'bottom'

    def corners_checks():
        if up == 'floor' and up_right == 'floor' and right == 'floor' and left == 'wall' and down == 'wall':
            return 'bottom_left_corner'
        #TODO
        #дописать углы
        if down == 'floor' and down_right == 'floor' and right == 'floor' and left == 'wall' and up == 'wall':
            return 'top'
        if up == 'wall' and right == 'wall' and up_right == 'floor':
            return 'bottom_right_corner'
        return None
    
    if corners_checks() == None:
        return wall_checks()
    return corners_checks()

def generate_tile_entities_from_template(template_path: str, factory: "EntityFactory"):
    """Генерирует сущности тайлов из шаблона"""
    template = pygame.image.load(template_path).convert_alpha()
    width, height = template.get_size()
    pixel_array = pygame.PixelArray(template)
    
    for x in range(width):
        for y in range(height):
            pixel_value = pixel_array[x, y]
            color = pygame.Color(*template.unmap_rgb(pixel_value))
            tile_type = get_tile_type_by_color((color.r, color.g, color.b, color.a))
            
            if tile_type != 'empty':
                walkable = (tile_type == 'floor')
                if tile_type == 'wall':
                    variant = get_tile_variant(x, y, pixel_array, width, height)
                else:  # floor
                    variant = random.choice(settings.TileMap.FLOOR_TILES)
                
                factory.create_tile(x, y, tile_type, variant, walkable)
    
    del pixel_array
