
from enum import Enum
from enums import CellState, Direction
from movement_handler import MovementHandler
from snake import Snake
from score_manager import ScoreManager
import random

class Environment:

    def __init__(self, dimensions: tuple = (20, 20), snake_start_position = [(10, 10)]):
        self.snake = Snake(snake_start_position) 
        self.movement_handler = MovementHandler()
        self.score_manager = ScoreManager()
        self.dimension = dimensions
        self.is_alive = True
        self.game_area = [[CellState.EMPTY for _ in range(self.dimension[0])] for _ in range(self.dimension[1])]
        self.fruits_locations = []
        for position in self.snake.get_body_parts():
            self.game_area[position[0]][position[1]] = CellState.SNAKE
        self.random_food_spawn()
        
    def spawn_food(self, position: tuple) -> bool:
        if self.game_area[position[0]][position[1]] == CellState.EMPTY:
            self.game_area[position[0]][position[1]] = CellState.FOOD
        return self.game_area[position[0]][position[1]] == CellState.FOOD

    def random_food_spawn(self):
        if self.fruits_locations:
            return # Non generare nuovo cibo se ce n'è già uno presente`
        
        number_of_food = random.choices([1, 2, 3], weights=[0.70, 0.20, 0.10])[0]
        for _ in range(number_of_food):
            while True:
                position = (random.randint(0, self.dimension[0] - 1), random.randint(0, self.dimension[1] - 1))
                if self.spawn_food(position):
                    self.fruits_locations.append(position)
                    break

    def get_game_area(self):
        return self.game_area

    def get_area_dimensions(self):
        return self.dimension

    def update_game_area(self):
        # Aggiorna la matrice del gioco dopo il movimento del serpente
        self.game_area = [[CellState.EMPTY for _ in range(self.dimension[0])] for _ in range(self.dimension[1])]
        for position in self.snake.get_body_parts():
            self.game_area[position[0]][position[1]] = CellState.SNAKE
        for position in self.fruits_locations:
            self.game_area[position[0]][position[1]] = CellState.FOOD

    def move_snake(self, direction):
        next_head_position = self.movement_handler.get_next_position(direction, snake_head_position=self.snake.get_head())
        if not self.is_valid_move(next_head_position):
            print ("Game Over! Collision detected.")
            self.is_alive = False
            return
        is_eating_food = next_head_position in self.fruits_locations
        self.snake.move(next_head_position, grow=is_eating_food)
        if is_eating_food:
            self.eat_food_if_present(next_head_position)
        self.update_game_area()

    def is_valid_move(self, next_head_position: tuple):
 
        if self.is_out_of_bounds(next_head_position):
            return False
    
        if self.is_colliding_with_self(next_head_position):
            return False
        
        return True

    def is_out_of_bounds(self, new_head_position: tuple) -> bool:
        # Controlla se la nuova posizione della testa è fuori dai limiti dell'ambiente
        if (new_head_position[0] < 0 or new_head_position[0] >= self.dimension[0] or
            new_head_position[1] < 0 or new_head_position[1] >= self.dimension[1]):
            return True
        return False
    
    def is_colliding_with_self(self, new_head_position: tuple) -> bool:
        # Controlla se la nuova posizione della testa collide con il corpo del serpente
        return new_head_position in self.snake.get_body_parts()

    def eat_food_if_present(self, new_head_position: tuple):
        self.score_manager.increase_score(1)  # Incrementa il punteggio di 1
        self.fruits_locations.remove(new_head_position)
        self.random_food_spawn()  # Genera un nuovo cibo in una posizione casuale

    def reset_environment(self):
        self.snake = Snake([(10, 10)])  # Reset del serpente alla posizione iniziale
        self.score_manager.reset_score()  # Reset del punteggio
        self.game_area = [[CellState.EMPTY for _ in range(self.dimension[0])] for _ in range(self.dimension[1])]
        self.fruits_locations = []
        self.previous_score = 0  # Reset del punteggio precedente
        self.previous_direction = None  # Reset della direzione precedente
        self.random_food_spawn()  # Genera un nuovo cibo in una posizione casuale
        self.is_alive = True  # Reset dello stato di vita del serpente
