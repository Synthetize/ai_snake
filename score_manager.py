class ScoreManager:
    """
    Manages tracking, increasing, and resetting the game score.
    """

    def __init__(self):
        self._score = 0

    @property
    def score(self) -> int:
        """Returns the current score in read-only mode."""
        return self._score

    def increase(self, points: int = 1):
        """Increases the current score by the given amount."""
        self._score += points

    def reset(self):
        """Resets the score back to zero."""
        self._score = 0
