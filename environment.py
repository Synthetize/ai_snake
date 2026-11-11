import random
from enums import CellState, Direction
from movement_handler import MovementHandler
from snake import Snake
from score_manager import ScoreManager


class Environment:
    """
    Represents the Snake game environment: grid, coordinates,
    cell states, collision checks, and interactions between the snake and food.
    """

    # -------------------------------------------------------------------------
    # Initialization and Reset
    # -------------------------------------------------------------------------

    def __init__(self, dimensions: tuple[int, int] = (20, 20), snake_start_position: list[tuple[int, int]] = [(10, 10)]):
        self.rows, self.cols = dimensions
        self.dimensions = (self.rows, self.cols)
        self.initial_snake_position = snake_start_position
        self.movement_handler = MovementHandler()
        self.score_manager = ScoreManager()

        self.reset_environment()

    def reset_environment(self):
        """Resets the environment back to a clean initial state."""
        self.snake = Snake(self.initial_snake_position)
        self.score_manager.reset()
        self.game_area = [[CellState.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.fruits_locations = []

        # Place initial snake body onto the grid
        for row, col in self.snake.body_parts:
            self.game_area[row][col] = CellState.SNAKE

        self.random_food_spawn()
        self.is_alive = True

    # -------------------------------------------------------------------------
    # Public Properties
    # -------------------------------------------------------------------------

    @property
    def score(self) -> int:
        """Returns the current score of the game."""
        return self.score_manager.score

    # -------------------------------------------------------------------------
    # Movement and Game Logic
    # -------------------------------------------------------------------------

    def move_snake(self, direction: Direction):
        """
        Computes the next position, checks collisions,
        moves the snake, and handles food consumption if applicable.
        """
        next_head = self.movement_handler.get_next_position(direction, snake_head_position=self.snake.head)

        if not self.is_valid_move(next_head):
            print("Game Over! Collision detected.")
            self.is_alive = False
            return

        old_tail = self.snake.tail
        is_eating_food = next_head in self.fruits_locations

        self.snake.move(next_head, grow=is_eating_food)

        if is_eating_food:
            self._eat_food(next_head)

        self._update_game_area(new_head=next_head, old_tail=old_tail, grow=is_eating_food)

    # -------------------------------------------------------------------------
    # Collisions and Validation
    # -------------------------------------------------------------------------

    def is_valid_move(self, next_head: tuple[int, int]) -> bool:
        """Checks whether a planned move results in a collision."""
        if self.is_out_of_bounds(next_head):
            return False

        if self.is_colliding_with_self(next_head):
            return False

        return True

    def is_out_of_bounds(self, position: tuple[int, int]) -> bool:
        """Verifies if the position lies outside the grid boundaries."""
        row, col = position
        return row < 0 or row >= self.rows or col < 0 or col >= self.cols

    def is_colliding_with_self(self, next_head: tuple[int, int]) -> bool:
        """
        Checks if the next head position collides with the snake's body.
        """
        body = self.snake.body_parts
        return next_head in body

    # -------------------------------------------------------------------------
    # Food Management
    # -------------------------------------------------------------------------

    def random_food_spawn(self):
        """Randomly spawns a cluster of 1 to 3 fruits on available empty cells."""
        if self.fruits_locations:
            return  # Do not spawn new food if any is still on the board

        number_of_food = random.choices([1, 2, 3], weights=[0.70, 0.20, 0.10])[0]
        empty_cells = [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if self.game_area[row][col] == CellState.EMPTY
        ]

        if empty_cells:
            k = min(number_of_food, len(empty_cells))
            chosen_positions = random.sample(empty_cells, k)
            for pos in chosen_positions:
                self._spawn_food_at(pos)

    def _spawn_food_at(self, food_position: tuple[int, int]):
        """Places a fruit on the grid and adds its coordinates to the list."""
        food_row, food_col = food_position
        if self.game_area[food_row][food_col] == CellState.EMPTY:
            self.game_area[food_row][food_col] = CellState.FOOD
            self.fruits_locations.append(food_position)

    def _eat_food(self, food_position: tuple[int, int]):
        """Handles the event when the snake eats a fruit."""
        self.score_manager.increase(1)
        self.fruits_locations.remove(food_position)
        self.random_food_spawn()

    # -------------------------------------------------------------------------
    # Internal Matrix Update
    # -------------------------------------------------------------------------

    def _update_game_area(self, new_head: tuple[int, int] = None, old_tail: tuple[int, int] = None, grow: bool = False):
        """Updates mutated cells in O(1) time (new head and cleared old tail)."""
        if new_head:
            head_row, head_col = new_head
            self.game_area[head_row][head_col] = CellState.SNAKE

        if old_tail and not grow:
            tail_row, tail_col = old_tail
            self.game_area[tail_row][tail_col] = CellState.EMPTY
