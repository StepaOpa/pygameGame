import pygame
import random
import settings
from assets import AssetManager
import debug
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
        return None
    
    if corners_checks() == None:
        return wall_checks()
    return corners_checks()

    # Если не определили особый случай, выбираем по наличию пола
    if left == 'floor':
        return 'left'
    if right == 'floor':
        return 'right'
    if up == 'floor':
        return 'top'
    if down == 'floor':
        return 'bottom'

    return 'empty' 

def generate_tilemap_from_template(template_path):
    """Генерирует карту из шаблона"""
    template = pygame.image.load(template_path).convert_alpha()
    width, height = template.get_size()
    pixel_array = pygame.PixelArray(template)
    
    tilemap = [[None] * height for _ in range(width)]
    
    for x in range(width):
        for y in range(height):
            pixel_value = pixel_array[x, y]
            # Преобразуем значение пикселя в RGBA
            color = pygame.Color(*template.unmap_rgb(pixel_value))
            tile_type = get_tile_type_by_color((color.r, color.g, color.b, color.a))
            
            if tile_type != 'empty':
                if tile_type == 'wall':
                    variant = get_tile_variant(x, y, pixel_array, width, height)
                else:  # floor
                    variant = random.choice(settings.TileMap.FLOOR_TILES)
                
                tilemap[x][y] = {
                    'type': tile_type,
                    'variant': variant
                }
    
    del pixel_array
    return tilemap

def render_tilemap(tilemap_component, surface, assets: AssetManager):
    """Отрисовывает карту на поверхности"""
    tilemap = tilemap_component.cached_tilemap
    cell_size = tilemap_component.cell_size

    for x in range(len(tilemap)):
        for y in range(len(tilemap[0])):
            tile_data = tilemap[x][y]
            if tile_data is not None:
                variant = tile_data['variant']
                if tile_data['type'] == 'floor':
                    sprite = assets.get_sprite(variant)
                else:
                    sprite = assets.get_tile_sprite(variant)
                
                if sprite:
                    scaled_sprite = tilemap_component.get_scaled_sprite(sprite, cell_size)
                    surface.blit(scaled_sprite, (x * cell_size, y * cell_size))
                else:
                    # Fallback to colored rectangle if sprite not found
                    pygame.draw.rect(surface, settings.TileMap.COLORS[tile_data['type']], 
                                  pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
