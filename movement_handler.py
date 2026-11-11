from enums import Direction

# Vector offsets (delta_row, delta_col) for each movement direction
DIRECTIONS_OFFSET = {
    Direction.UP:    (-1,  0),  # row - 1, col + 0
    Direction.DOWN:  ( 1,  0),  # row + 1, col + 0
    Direction.LEFT:  ( 0, -1),  # row + 0, col - 1
    Direction.RIGHT: ( 0,  1),  # row + 0, col + 1
}


class MovementHandler:
    """
    Handles kinematic coordinate calculations for discrete grid movement.
    """

    def __init__(self):
        pass

    def get_next_position(self, direction: Direction, snake_head_position: tuple[int, int]) -> tuple[int, int]:
        """
        Given a direction and the current head position (row, col),
        returns the resulting target coordinates (row, col).
        """
        head_row, head_col = snake_head_position
        delta_row, delta_col = DIRECTIONS_OFFSET[direction]
        return (head_row + delta_row, head_col + delta_col)
