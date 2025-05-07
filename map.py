import pygame
import random
import utils
import settings


class Tilemap:
    def __init__(self, map_template_image: pygame.surface.Surface, tiles: dict[str: tuple[str]]):
        self.tile_size = settings.Map.TILE_SIZE
        self.template_size = settings.Map.TEMPLATE_SIZE
        self.offset = pygame.Vector2(0, 0)
        self.tiles = tiles
        self.map_template_image = map_template_image
        self.cached_map = self._generate_map()

    def get_colors_from_template(self):
        colors = settings.Map.COLORS
        colors_reversed = {v: k for k, v in colors.items()}
        pixel_matrix = [[None for _ in range(
            self.template_size)] for _ in range(self.template_size)]
        for y in range(self.template_size):
            for x in range(self.template_size):
                pixel_matrix[y][x] = self.map_template_image.get_at((x, y))
                if tuple(pixel_matrix[y][x]) in colors.values():
                    pixel_matrix[y][x] = colors_reversed.get(
                        tuple(pixel_matrix[y][x]))
        return pixel_matrix  # матрица цветов попиксельно

    def _generate_map(self):
        generated = []
        for y, row in enumerate(self.get_colors_from_template()):
            new_row = []
            for x, color in enumerate(row):
                if color == 'BROWN':  # Пол
                    new_row.append(random.choice(self.tiles['floor']))
                elif color == 'BLUE':  # Стена
                    new_row.append(random.choice(self.tiles['walls']))
                else:
                    new_row.append(None)
            generated.append(new_row)
        return generated

    def render(self, surface: pygame.surface.Surface):
        for y, row in enumerate(self.cached_map):
            for x, tile in enumerate(row):
                if tile:
                    pos = (x * self.tile_size - self.offset.x,
                           y * self.tile_size - self.offset.y)
                    surface.blit(tile, pos)


def test():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    screen.fill((255, 255, 255))
    tiles = {tile_type: [utils.load_image(path) for path in paths]
             for tile_type, paths in settings.Map.TILES.items()}
    tilemap = Tilemap(utils.load_image(
        'Map/chunk_templates/chunck_template_0.png'), tiles)
    pixel_data = tilemap.get_colors_from_template()
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
