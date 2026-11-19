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
        self.direction = Direction.RIGHT
        # Place initial snake body onto the grid
        for row, col in self.snake.body_parts:
            self.game_area[row][col] = CellState.SNAKE

        self.random_food_spawn()
        self.is_alive = True
        self.steps_without_food = 0 

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

        self.direction = direction
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
        row, col = next_head
        return self.game_area[row][col] == CellState.SNAKE

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



    # -------------------------------------------------------------------------



    def get_state(self) -> list[int]:
        clock_wise_directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        direction_idx = clock_wise_directions.index(self.direction)

        head_row, head_col = self.snake.head

  
        dir_straight = clock_wise_directions[direction_idx]
        dir_left = clock_wise_directions[(direction_idx - 1) % 4]
        dir_right = clock_wise_directions[(direction_idx + 1) % 4]

        #next move points based on current direction
        point_straight = self.movement_handler.get_next_position(dir_straight, (head_row, head_col))
        point_left = self.movement_handler.get_next_position(dir_left, (head_row, head_col))
        point_right = self.movement_handler.get_next_position(dir_right, (head_row, head_col))

        straight_danger = not self.is_valid_move(point_straight)
        left_danger = not self.is_valid_move(point_left)
        right_danger = not self.is_valid_move(point_right)

        nearest_food = self.get_nearest_food()
        food_row, food_col = nearest_food if nearest_food else (head_row, head_col)  # Default to head position if no food

        # Dynamic reachable space: the tail frees up as the snake moves.
        # Normalized by the number of currently free cells -> value in [0, 1].
        body = self.snake.body_length
        release_times = self.movement_handler.build_release_times(body, self.rows, self.cols)
        free_cells = max(1, self.rows * self.cols - len(body))

        def space(point):
            reachable = self.movement_handler.count_reachable_space(point, self.rows, self.cols, release_times)
            return min(1.0, reachable / free_cells)

        right_space = space(point_right)
        left__space = space(point_left)
        straight_space = space(point_straight)

        return  [
            int(straight_danger),
            int(right_danger),
            int(left_danger),

            int(self.direction == Direction.UP),
            int(self.direction == Direction.RIGHT),
            int(self.direction == Direction.DOWN),
            int(self.direction == Direction.LEFT),

            int(food_row < head_row),  # food up
            int(food_row > head_row),  # food down
            int(food_col < head_col),  # food left
            int(food_col > head_col),  # food right

            float(straight_space),  # reachable space straight ahead
            float(right_space),  # reachable space to the right
            float(left__space),  # reachable space to the left
        ]  

    def get_nearest_food(self):
        """Returns the coordinates of the nearest fruit to the snake's head."""
        head_row, head_col = self.snake.head
        return  min(self.fruits_locations, key=lambda f: abs(f[0] - head_row) + abs(f[1] - head_col))

    def step(self, action: list[float]):
        clock_wise = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        idx = clock_wise.index(self.direction)
        if action == [1, 0, 0]:  # straight
            new_dir = clock_wise[idx]
        elif action == [0, 1, 0]:  # right turn
            new_dir = clock_wise[(idx + 1) % 4]
        else:  # left turn
            new_dir = clock_wise[(idx - 1) % 4]

        old_score = self.score

        reward_by_distance = self.reward_for_distance_change(new_dir)

        self.move_snake(new_dir)

        max_allowed_steps = 100 * len(self.snake.body_length)  # Allow more steps as the snake grows

        if not self.is_alive:
            reward = -10
            done = True
        elif self.score > old_score:
            reward = 10
            done = False
            self.steps_without_food = 0  # Reset the counter when food is eaten
        else:
            if self.steps_without_food > max_allowed_steps:  # If the snake hasn't eaten food for 100 steps, end the game
                reward = -10
                done = True
            else:
                reward = reward_by_distance
                self.steps_without_food += 1
                done = False

        return self.get_state(), reward, done, self.score

    def get_distance_to_nearest_food(self, head_position: tuple[int, int]) -> int:
        """Calculates the Manhattan distance from the snake's head to the nearest fruit."""
        nearest_food = self.get_nearest_food()
        if nearest_food:
            head_row, head_col = head_position
            food_row, food_col = nearest_food
            return abs(food_row - head_row) + abs(food_col - head_col)
        return 0  # No food available

    def reward_for_distance_change(self, new_dir: Direction) -> float:
        old_distance = self.get_distance_to_nearest_food(self.snake.head)
        new_distance = self.get_distance_to_nearest_food(self.movement_handler.get_next_position(new_dir, self.snake.head))
        if new_distance < old_distance:
            return 0.1  # Reward for moving closer to food
        elif new_distance > old_distance:
            return -0.15  # Penalty for moving away from food 
        else:
            return -0.05  # No change in distance