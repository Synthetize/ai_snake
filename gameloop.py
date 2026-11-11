import pygame
from environment import Environment
from enums import Direction, CellState


class GameLoop:
    """
    Game loop controller for human play:
    handles keyboard inputs, ticks the environment,
    renders frames via Pygame, and manages adaptive game speed.
    """

    def __init__(self, cell_size: int = 20):
        self.environment = Environment()
        self.num_rows, self.num_cols = self.environment.dimensions
        self.cell_size = cell_size
        self.previous_direction = Direction.RIGHT
        self.current_direction = Direction.RIGHT

        # ---------------------------------------------------------------------
        # Pygame Initialization
        # ---------------------------------------------------------------------
        pygame.init()
        screen_width = self.num_cols * self.cell_size
        screen_height = self.num_rows * self.cell_size
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Snake AI - Human Mode")
        self.clock = pygame.time.Clock()

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)

        self.running = True

    # -------------------------------------------------------------------------
    # Main Game Loop
    # -------------------------------------------------------------------------

    def run(self):
        """Continuous execution loop: Events -> Update -> Draw -> Tick."""
        while self.running:
            self._check_game_over()
            self._handle_events()
            self._update()
            self._draw(self.environment.game_area)

            # Dynamic difficulty: speed scales up with score (capped at 20 FPS)
            current_score = self.environment.score
            speed = min(20.0, 4.0 + current_score * 0.2)
            self.clock.tick(int(speed))

        pygame.quit()

    # -------------------------------------------------------------------------
    # Event and Input Handling
    # -------------------------------------------------------------------------

    def _handle_events(self):
        """Processes keyboard inputs and window termination events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.current_direction = Direction.UP
                elif event.key == pygame.K_s:
                    self.current_direction = Direction.DOWN
                elif event.key == pygame.K_a:
                    self.current_direction = Direction.LEFT
                elif event.key == pygame.K_d:
                    self.current_direction = Direction.RIGHT

    def _restart_game(self):
        """Resets the game state and environment for a new session."""
        self.environment.reset_environment()
        self.current_direction = Direction.RIGHT
        self.previous_direction = Direction.RIGHT

    # -------------------------------------------------------------------------
    # Game Logic Update
    # -------------------------------------------------------------------------

    def _update(self):
        """Checks game over status, prevents 180-degree instant turns, and advances the snake."""
        if not self.environment.is_alive:
            # Reset environment when snake dies
            self.environment.reset_environment()
            self.current_direction = Direction.RIGHT
            self.previous_direction = Direction.RIGHT
            return

        # Prevent 180-degree immediate reversal into own neck
        is_vertical_reverse = (
            (self.current_direction is Direction.UP and self.previous_direction is Direction.DOWN) or
            (self.current_direction is Direction.DOWN and self.previous_direction is Direction.UP)
        )
        is_horizontal_reverse = (
            (self.current_direction is Direction.LEFT and self.previous_direction is Direction.RIGHT) or
            (self.current_direction is Direction.RIGHT and self.previous_direction is Direction.LEFT)
        )

        if is_vertical_reverse or is_horizontal_reverse:
            self.current_direction = self.previous_direction

        self.environment.move_snake(self.current_direction)
        self.previous_direction = self.current_direction

    def _check_game_over(self):
        """If the snake is dead, display a game over message and wait for a key press."""
        if not self.environment.is_alive:
            self._draw_game_over()
            #wait 3 seconds before resetting
            pygame.time.delay(3000)
            self._restart_game()
            

    # -------------------------------------------------------------------------
    # Graphical Rendering
    # -------------------------------------------------------------------------

    def _draw(self, matrix: list[list[CellState]]):
        """Draws the entire frame: background, grid lines, cells, and UI score."""
        self.screen.fill((0, 0, 0))
        self._draw_grid()

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell = matrix[row][col]
                if cell == CellState.SNAKE:
                    color = (0, 255, 0)
                elif cell == CellState.FOOD:
                    color = (255, 0, 0)
                else:
                    continue

                pixel_x = col * self.cell_size
                pixel_y = row * self.cell_size
                pygame.draw.rect(self.screen, color, (pixel_x, pixel_y, self.cell_size, self.cell_size))

        self._draw_score()
        pygame.display.flip()

    def _draw_score(self):
        """Renders the score text in the top-left corner."""
        score = self.environment.score
        score_surface = self.font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 10))

    def _draw_grid(self):
        """Draws subtle divider grid lines on the screen."""
        color = (40, 40, 40)

        # Vertical lines
        for col in range(self.num_cols + 1):
            pixel_x = col * self.cell_size
            pygame.draw.line(self.screen, color, (pixel_x, 0), (pixel_x, self.num_rows * self.cell_size))

        # Horizontal lines
        for row in range(self.num_rows + 1):
            pixel_y = row * self.cell_size
            pygame.draw.line(self.screen, color, (0, pixel_y), (self.num_cols * self.cell_size, pixel_y))

    def _draw_game_over(self):
        """Displays a game over message in the center of the screen."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black overlay
        self.screen.blit(overlay, (0, 0))

        game_over_surface = self.font.render("Game Over!", True, (255, 0, 0))
        score_surface = self.font.render(f"Final Score: {self.environment.score}", True, (255, 255, 255))

        # Center the text
        game_over_rect = game_over_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 20))
        score_rect = score_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))

        self.screen.blit(game_over_surface, game_over_rect)
        self.screen.blit(score_surface, score_rect)
        pygame.display.flip()
       