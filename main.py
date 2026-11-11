from gameloop import GameLoop

if __name__ == "__main__":
    # Entry point for human playable mode using Pygame
    game = GameLoop(cell_size=20)
    game.run()
