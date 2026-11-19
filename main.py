import sys
from gameloop import GameLoop
from agent import train_visual

if __name__ == "__main__":
    # If launched with 'ai' argument: python main.py ai
    # Otherwise defaults to AI mode if you want to watch it right away!
    if len(sys.argv) > 1 and sys.argv[1].lower() == "human":
        print("Starting Human Mode... (W, A, S, D to control)")
        game = GameLoop(cell_size=20)
        game.run()
    else:
        print("Starting AI Training Mode with Real-Time Neural Network Visualization...")
        print("(Run 'python main.py human' if you want to play manually)")
        train_visual(fps=60)
