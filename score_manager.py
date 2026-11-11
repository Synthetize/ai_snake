class ScoreManager:
    def __init__(self):
        self.score = 0

    def increase_score(self, points: int):
        self.score += points

    def get_score(self) -> int:
        return self.score

    def reset_score(self):
        self.score = 0