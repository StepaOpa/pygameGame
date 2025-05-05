import pygame
import random
import utils


class Tilemap:
    def __init__(self, level_map: tuple[int], tiles: dict[str: tuple[pygame.surface.Surface]]):
        self.tile_size = 16
        self.offset = pygame.Vector2(0, 0)
        self.level_map = level_map
        self.tiles = tiles
        self.needs_redraw = False
        self.cached_surface = None
        self.generated_map = self._generate_map()

    def get_map_from_template(self, template_image: pygame.surface.Surface):
        pixel_matrix = [[None for _ in range(32)] for _ in range(32)]
        for y in range(32):
            for x in range(32):
                pixel_matrix[y][x] = template_image.get_at((x, y))
        # print(pixel_matrix)
        return pixel_matrix

    def _generate_map(self):
        generated = []
        for y, row in enumerate(self.level_map):
            new_row = []
            for x, tile_id in enumerate(row):
                if tile_id == 1:  # Пол
                    new_row.append(random.choice(self.tiles['floor']))
                elif tile_id == 2:  # Стена
                    new_row.append(self.tiles['wall'][0])
                else:
                    new_row.append(None)
            generated.append(new_row)
        return generated

    def render(self, surface: pygame.surface.Surface):
        for y, row in enumerate(self.generated_map):
            for x, tile in enumerate(row):
                if tile:
                    pos = (x * self.tile_size - self.offset.x,
                           y * self.tile_size - self.offset.y)
                    surface.blit(tile, pos)


def test_map_from_template():
    pygame.init()
    dummy_map = [[0]*32 for _ in range(32)]
    dummy_tiles = {'floor': [pygame.Surface((16, 16))], 'wall': [
        pygame.Surface((16, 16))]}
    tilemap = Tilemap(dummy_map, dummy_tiles)

    screen = pygame.display.set_mode((400, 400))
    screen.fill((255, 255, 255))

    pixel_data = tilemap.get_map_from_template(utils.load_image(
        'Map/chunk_templates/chunck_template_0.png'))

    for y in range(32):
        for x in range(32):
            pygame.draw.rect(screen, pixel_data[y][x], (x*2, y*2, 2, 2))

    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


if __name__ == '__main__':
    template = test_map_from_template()
    print(template[0])
