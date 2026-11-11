from enum import Enum


class CellState(Enum):
    EMPTY = 0
    SNAKE = 1
    FOOD = 2

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
