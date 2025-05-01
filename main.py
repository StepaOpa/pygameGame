import pygame
import sys
from settings import Display

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('MyGame')
        self._screen = pygame.display.set_mode((Display.WIDTH, Display.HEIGHT))    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._screen.fill(Display.BACKGROUND_COLOR)

            pygame.display.flip()

Game().run()
