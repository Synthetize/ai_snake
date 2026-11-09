
from collections import deque

class Snake:

    def __init__(self, default_positions: list[tuple]):
        self.body_lenght = deque(default_positions)
        
    def get_body_parts(self):
        return list(self.body_lenght)

    def get_head(self):
        return self.body_lenght[0]

    def add_body_part(self, position):
        self.body_lenght.appendleft(position)  # Aggiungi una nuova parte del corpo alla fine della deque

    def move(self, new_head_position):
        if new_head_position in self.body_lenght:
            raise Exception("Game Over: The snake collided with itself!")  # Controlla se la nuova posizione della testa collide con il corpo del serpente
        self.body_lenght.appendleft(new_head_position)  # Aggiungi la nuova testa all'inizio della deque
        self.body_lenght.pop()  # Rimuovi l'ultimo elemento della deque per simulare il movimento
