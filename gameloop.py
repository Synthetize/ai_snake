import pygame
from environment import Environment
from enums import Direction, CellState

class GameLoop:

    previous_direction = None
    current_direction = None

    def __init__(self, cell_size: int = 20):
        self.speed = 4  # Velocità del gioco (frame per secondo)
        self.environment = Environment()
        self.dimensions = self.environment.get_area_dimensions()
        self.cell_size = cell_size
        self.previous_direction = Direction.RIGHT  # Direzione iniziale del serpente
        self.current_direction = Direction.RIGHT  # Direzione iniziale del serpente
        self.previous_score = 0
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.dimensions[0] * self.cell_size, self.dimensions[1] * self.cell_size))
        self.clock = pygame.time.Clock()

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)

        self.running = True
    
    def run(self):
        while self.running:
            self._check_game_over()
            self._handle_events()
            self._update()
            self._draw(self.environment.get_game_area())
            self.check_for_speed_increase()

            self.clock.tick(self.speed)  # Limit to 60 frames per second

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.current_direction = Direction.UP
                if event.key == pygame.K_s:
                    self.current_direction = Direction.DOWN
                if event.key == pygame.K_a:
                    self.current_direction = Direction.LEFT
                if event.key == pygame.K_d:
                    self.current_direction = Direction.RIGHT

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
                self._draw_score() 
        pygame.display.flip()

    def _draw_score(self):
            score_surface = self.font.render(f"Score: {self.environment.score_manager.get_score()}", True, (255, 255, 255))  # bianco
            self.screen.blit(score_surface, (10, 10))  # disegna in alto

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

    def _draw_game_over(self):
        game_over_surface = self.font.render("Game Over!", True, (255, 0, 0))  # rosso
        score_surface = self.font.render(f"Final Score: {self.environment.score_manager.get_score()}", True, (255, 255, 255))  # bianco
        self.screen.blit(game_over_surface, (self.dimensions[0] * self.cell_size // 2 - game_over_surface.get_width() // 2,
                                              self.dimensions[1] * self.cell_size // 2 - game_over_surface.get_height()))
        self.screen.blit(score_surface, (self.dimensions[0] * self.cell_size // 2 - score_surface.get_width() // 2,
                                          self.dimensions[1] * self.cell_size // 2 + score_surface.get_height()))
        pygame.display.flip()

    def _undraw_game_over(self):
        self.screen.fill((0, 0, 0))  # sfondo nero
        self._draw_grid()
        pygame.display.flip()

    def _update(self):
        if (self.current_direction is Direction.UP and self.previous_direction is Direction.DOWN) or (self.current_direction is Direction.DOWN and self.previous_direction is Direction.UP):
            self.current_direction = self.previous_direction  # Mantieni la direzione precedente
            self.environment.move_snake(self.current_direction)  # Muovi il serpente nella direzione precedente
            return  # Non fare nulla se la direzione è la stessa o opposta

        
        elif (self.current_direction is Direction.LEFT and self.previous_direction is Direction.RIGHT) or (self.current_direction is Direction.RIGHT and self.previous_direction is Direction.LEFT):
            self.current_direction = self.previous_direction  # Mantieni la direzione precedente
            self.environment.move_snake(self.current_direction)  # Muovi il serpente nella dire
            return  # Non fare nulla se la direzione è la stessa o opposta


        self.environment.move_snake(self.current_direction)
        self.previous_direction = self.current_direction

    def check_for_speed_increase(self):
        if self.previous_score < self.environment.score_manager.get_score():
            print(f"Increasing speed")
            self.previous_score = self.environment.score_manager.get_score()
            self.speed = min(15, self.speed + 0.2)  # Incrementa la velocità, ma non oltre 10

    def _check_game_over(self):
        if not self.environment.is_alive:
            self._draw_game_over()
            wait_time = 3000  # Tempo di attesa in millisecondi (3 secondi)
            pygame.time.wait(wait_time)
            self._undraw_game_over()
            self.speed = 4  # Reset della velocità
            self.previous_score = 0  # Reset del punteggio precedente
            self.previous_direction = None  # Reset della direzione precedente
            self.environment.reset_environment()
