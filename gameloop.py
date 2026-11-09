import pygame
from environment import Environment, CellState

class GameLoop:

    def __init__(self, cell_size: int = 20):
        self.environment = Environment()
        self.dimensions = self.environment.get_area_dimensions()
        self.cell_size = cell_size
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.dimensions[0] * self.cell_size, self.dimensions[1] * self.cell_size))
        self.clock = pygame.time.Clock()

        self.running = True
    
    def run(self):
        while self.running:
            self._handle_events()
            self._draw(self.environment.get_game_area())
            self.clock.tick(10)  # Limit to 60 frames per second

    def _handle_events(self):
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.environment.move_snake("up")
                if event.key == pygame.K_s:
                    self.environment.move_snake("down")
                if event.key == pygame.K_a:
                    self.environment.move_snake("left")
                if event.key == pygame.K_d:
                    self.environment.move_snake("right")

    def _draw(self, matrix):
        self.screen.fill((0, 0, 0))  # sfondo nero
        self._draw_grid()
        for row in range(self.dimensions[1]):
            for col in range(self.dimensions[0]):
                cell = matrix[row][col]
                if cell == CellState.SNAKE:
                    color = (0, 255, 0)    # verde
                elif cell == CellState.FOOD:
                    color = (255, 0, 0)    # rosso
                else:
                    continue               # cella vuota, non disegnare nulla
                # converti coordinate griglia → pixel
                x = col * self.cell_size
                y = row * self.cell_size
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))
        pygame.display.flip()

    def _draw_grid(self):
        color = (40, 40, 40)  # grigio scuro, quasi invisibile
    
        # Linee verticali
        for col in range(self.dimensions[0] + 1):
            x = col * self.cell_size
            pygame.draw.line(self.screen, color, (x, 0), (x, self.dimensions[1] * self.cell_size))

        # Linee orizzontali
        for row in range(self.dimensions[1] + 1):
            y = row * self.cell_size
            pygame.draw.line(self.screen, color, (0, y), (self.dimensions[0] * self.cell_size, y))