import pygame
import random
import settings
import assets


class Tilemap:
    def __init__(self, asset_manager: assets.AssetManager):
        self.asset_manager = asset_manager
        self.tile_size = asset_manager.tile_size
        self.template_size = asset_manager.template_size
        self.offset = pygame.Vector2(0, 0)
        self.map_template_image = asset_manager.get_chunk(
            'chunk_template_0')
        self.cached_map = self._generate_map()
        print(self.asset_manager.base_path)

    def get_colors_from_template(self) -> list[list[str]]:
        """Returns a matrix of colors from the map template image"""
        color_map = settings.Map.COLORS
        color_map_reversed = {v: k for k, v in color_map.items()}
        pixel_matrix = [[None for _ in range(self.template_size)]
                        for _ in range(self.template_size)]

        for y in range(self.template_size):
            for x in range(self.template_size):
                pixel = self.map_template_image.get_at((x, y))
                if tuple(pixel) in color_map.values():
                    pixel_matrix[y][x] = color_map_reversed.get(tuple(pixel))

        return pixel_matrix

    def _generate_map(self):
        generated = []
        c = 0
        color_matrix = self.get_colors_from_template()
        for y, row in enumerate(color_matrix):
            new_row = []
            for x, color in enumerate(row):
                if color == 'BROWN':  # floor
                    # new_row.append(random.choice(self.tiles['floor']))
                    new_row.append(self.asset_manager.get_random_tile('floor'))
                elif color == 'GREEN':
                    # walls
                    matrix_of_surrounding_pixels = [
                        surrounding_row[x-1:x+2] for surrounding_row in color_matrix[y-1:y+2]]
                    c += 1
                    new_row.append(self._wall_generator(
                        matrix_of_surrounding_pixels, coords=(x, y)))
                else:
                    new_row.append(None)
            generated.append(new_row)
        return generated

    def _wall_generator(self, matrix_of_surrounding_pixels: tuple[tuple[str]], coords):
        if matrix_of_surrounding_pixels[2][1] == 'BROWN':
            print('topwalls')
            return self.asset_manager.get_random_tile('top_walls')
        if matrix_of_surrounding_pixels[0][1] == 'BROWN':
            return self.asset_manager.get_random_tile('bottom_walls')
        if matrix_of_surrounding_pixels[1][2] == 'BROWN' \
            or (matrix_of_surrounding_pixels[1][2] == 'GREEN'
                and matrix_of_surrounding_pixels[2][1] == 'GREEN'
                and matrix_of_surrounding_pixels[1][0] != 'BROWN'
                and matrix_of_surrounding_pixels[2][2] == 'BROWN'):
            return self.asset_manager.get_random_tile('left_walls')
        if matrix_of_surrounding_pixels[1][0] == 'BROWN' \
            or (matrix_of_surrounding_pixels[1][0] == 'GREEN'
                and matrix_of_surrounding_pixels[2][1] == 'GREEN'):
            return self.asset_manager.get_random_tile('right_walls')
        if matrix_of_surrounding_pixels[1][0] == 'GREEN' \
            and matrix_of_surrounding_pixels[0][1] == 'GREEN' \
                and matrix_of_surrounding_pixels[0][0] == 'BROWN':
            return self.asset_manager.get_random_tile('corners')
        return self.asset_manager.get_random_tile('floor')

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
    asset_manager = assets.AssetManager()
    # tiles = {tile_type: [utils.load_image(path) for path in paths]
    #          for tile_type, paths in settings.Map.TILES.items()}
    tilemap = Tilemap(asset_manager)
    pixel_data = tilemap.get_colors_from_template()
    screen.fill(settings.ScreenSettngs.BACKGROUND_COLOR)

    # print(pixel_data)
    # print(tiles)
    # print(len(pixel_data[0]))
    # print(pixel_data[0])
    # print(pixel_data[0][0])
    running = True
    # print(tiles)
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
