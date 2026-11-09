
from typing import TYPE_CHECKING

from snake import Snake

if TYPE_CHECKING:
    from environment import Environment

class MovementHandler:
    def __init__(self, environment: "Environment"):
        self.snake = environment.snake
        self.environment = environment

    def handle_movement(self, direction):
        print(f"Current position of the snake's head: {self.snake.get_head()}")
        if direction == "up":
            head_position = self.snake.get_head()
            new_head_position = (head_position[0] - 1, head_position[1])
            if not self.environment.is_valid_move(new_head_position):
                raise Exception("Game Over: The snake collided with the wall or itself!")
            self.snake.move(new_head_position)
            self.environment.eat_food_if_present()

        elif direction == "down":
            head_position = self.snake.get_head()
            new_head_position = (head_position[0] + 1, head_position[1])
            if not self.environment.is_valid_move(new_head_position):
                raise Exception("Game Over: The snake collided with the wall or itself!")
            self.snake.move(new_head_position)
            self.environment.eat_food_if_present()

        elif direction == "left":
            head_position = self.snake.get_head()
            new_head_position = (head_position[0], head_position[1] - 1)
            if not self.environment.is_valid_move(new_head_position):
                raise Exception("Game Over: The snake collided with the wall or itself!")
            self.snake.move(new_head_position)
            self.environment.eat_food_if_present()

        elif direction == "right":
            head_position = self.snake.get_head()
            new_head_position = (head_position[0], head_position[1] + 1)
            if not self.environment.is_valid_move(new_head_position):
                raise Exception("Game Over: The snake collided with the wall or itself!")
            self.snake.move(new_head_position)
            self.environment.eat_food_if_present()