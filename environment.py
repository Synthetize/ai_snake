
from enum import Enum
from movement_handler import MovementHandler
from snake import Snake


class Environment:

    def __init__(self, dimensions: tuple = (20, 20), snake_start_position = [(10, 10), (10, 9), (10, 8), (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2), (10, 1), (10, 0)]):
        self.snake = Snake(snake_start_position)
        self.movement_handler = MovementHandler(self)
        self.dimension = dimensions
        self.game_area = [[CellState.EMPTY for _ in range(self.dimension[0])] for _ in range(self.dimension[1])]
        self.fruits_locations = []
        for position in self.snake.get_body_parts():
            self.game_area[position[0]][position[1]] = CellState.SNAKE
        self.random_food_spawn()
        
    def spawn_food(self, position: tuple) -> bool:
        if self.game_area[position[0]][position[1]] == CellState.EMPTY:
            self.game_area[position[0]][position[1]] = CellState.FOOD
        return self.game_area[position[0]][position[1]] == CellState.FOOD

    def random_food_spawn(self, number_of_food: int = 1):
        import random
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
        self.movement_handler.handle_movement(direction)
        self.update_game_area()

    def is_valid_move(self, new_head_position: tuple):
 
        if self.is_out_of_bounds(new_head_position):
            print(f"Invalid move to {new_head_position}: false")
            return False
    
        if self.is_colliding_with_self(new_head_position):
            print(f"Invalid move to {new_head_position}: true")
            return False
        
        print(f"Valid move to {new_head_position}: true")
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

    def eat_food_if_present(self):
        head_position = self.snake.get_head()
        if head_position in self.fruits_locations:
            self.fruits_locations.remove(head_position)
            self.snake.add_body_part(head_position)  # Aggiungi una nuova parte del corpo alla testa
            self.random_food_spawn()  # Genera un nuovo cibo in una posizione casuale
            return True
        return False
    


class CellState(Enum):
    EMPTY = 0
    SNAKE = 1
    FOOD = 2

