
from typing import TYPE_CHECKING

from enums import Direction
from snake import Snake

# if TYPE_CHECKING:
#     from environment import Environment

class MovementHandler:
    def __init__(self):
        pass

    def get_next_position(self, direction, snake_head_position: tuple) -> tuple:
        if direction == Direction.UP:
            return (snake_head_position[0] - 1, snake_head_position[1])

        elif direction == Direction.DOWN:
            return (snake_head_position[0] + 1, snake_head_position[1])

        elif direction == Direction.LEFT:
            return (snake_head_position[0], snake_head_position[1] - 1)

        elif direction == Direction.RIGHT:
            return (snake_head_position[0], snake_head_position[1] + 1)