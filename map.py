import pygame
import random
import utils
import settings


class Tilemap:
    def __init__(self, map_template_image: pygame.surface.Surface, tiles: dict[str: tuple[str]]):
        self.tile_size = 16
        self.offset = pygame.Vector2(0, 0)
        self.tiles = tiles
        self.map_template_image = map_template_image
        self.cached_surface = None

    def get_colors_from_template(self):
        colors = settings.Map.COLORS
        colors_reversed = {v: k for k, v in colors.items()}
        pixel_matrix = [[None for _ in range(32)] for _ in range(32)]
        for y in range(32):
            for x in range(32):
                pixel_matrix[y][x] = self.map_template_image.get_at((x, y))
                if tuple(pixel_matrix[y][x]) in colors.values():
                    pixel_matrix[y][x] = colors_reversed.get(
                        tuple(pixel_matrix[y][x]))
        return pixel_matrix  # матрица цветов попиксельно

    def render(self, surface: pygame.surface.Surface):
        for y, row in enumerate(self.get_colors_from_template()):
            for x, color in enumerate(row):
                for tile in self.tiles:
                    if color == 'BROWN' and tile == 'floor':
                        continue
                    if color != tile:
                        continue
                    pos = (x * self.tile_size, y * self.tile_size)
                    try:
                        # Получаем список вариантов тайлов
                        tile_variants = self.tiles[tile]
                        random_index = random.randint(
                            0, len(tile_variants) - 1)
                        selected_tile = tile_variants[random_index]
                        surface.blit(selected_tile, pos)
                    except KeyError:
                        print(
                            f"Ошибка: ключ '{tile}' отсутствует в tiles. Доступные ключи: {list(self.tiles.keys())}")
                    except IndexError:
                        print(f"Ошибка: список тайлов для '{tile}' пуст")


def test():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    screen.fill((255, 255, 255))
    tiles = {tile_type: [utils.load_image(path) for path in paths]
             for tile_type, paths in settings.Map.TILES.items()}
    tilemap = Tilemap(utils.load_image(
        'Map/chunk_templates/chunck_template_0.png'), tiles)
    pixel_data = tilemap.get_colors_from_template()
    # for y in range(32):
    #     for x in range(32):
    #         pygame.draw.rect(screen, pixel_data[y][x], (x*8, y*8, 8, 8))

    screen.fill(settings.Screen.BACKGROUND_COLOR)

    print(pixel_data)
    print(tiles)
    # print(len(pixel_data[0]))
    # print(pixel_data[0])
    # print(pixel_data[0][0])
    running = True
    while running:
        tilemap.render(screen)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()


if __name__ == "__main__":
    test()
    # tilemap = Tilemap()
    # print(tilemap.get_map_from_template(utils.load_image(
    #     'Map/chunk_templates/chunck_template_0.png')))
