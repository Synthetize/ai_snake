from collections import deque


class Snake:
    """
    Represents the snake entity.
    Manages the body data structure (deque of coordinates) and growth behavior.
    """

    def __init__(self, default_positions: list[tuple[int, int]]):
        # default_positions contains tuples of (row, col) coordinates.
        # Head is located at index 0, tail is at index -1.
        self.body_length = deque(default_positions)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def body_parts(self) -> list[tuple[int, int]]:
        """Returns a list of all body segment coordinates (row, col)."""
        return list(self.body_length)

    @property
    def head(self) -> tuple[int, int]:
        """Returns the current head coordinates (row, col)."""
        return self.body_length[0]

    @property
    def tail(self) -> tuple[int, int]:
        """Returns the current tail-tip coordinates (row, col)."""
        return self.body_length[-1]

    # -------------------------------------------------------------------------
    # Movement
    # -------------------------------------------------------------------------

    def move(self, new_head_position: tuple[int, int], grow: bool = False):
        """
        Advances the snake by prepending the new head position.
        If grow=False, pops the oldest tail segment.
        If grow=True, the tail segment is kept (the snake grows by 1).
        """
        self.body_length.appendleft(new_head_position)
        if not grow:
            self.body_length.pop()
