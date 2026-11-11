from enum import Enum


class CellState(Enum):
    """Represents the possible state of any individual grid cell."""
    EMPTY = 0
    SNAKE = 1
    FOOD = 2


class Direction(Enum):
    """Represents the four cardinal movement directions."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
