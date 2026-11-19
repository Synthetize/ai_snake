import random
from collections import deque
import pygame
import torch
from enums import CellState
from environment import Environment
from model import Linear_QNet, QTrainer
from neural_visualizer import NeuralVisualizer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
TRAIN_EVERY = 4  # Train once every N environment steps (instead of every step)
REPLAY_BATCH_SIZE = 64  # Mini-batch size for the periodic in-game training


class Agent:
    """
    Reinforcement Learning Agent driving the Snake using Deep Q-Learning (DQN).
    """

    def __init__(self):
        self.n_games = 0
        self.epsilon = 1.0  # Randomness factor (exploration rate)
        self.epsilon_decay = 0.995  # Decay rate for epsilon after each game
        self.epsilon_min = 0.01  # Minimum exploration rate
        self.gamma = 0.97  # Discount rate (longer horizon to avoid self-trapping)
        self.memory = deque(maxlen=MAX_MEMORY)  # Replay memory buffer

        # 14 input features, 256 -> 128 hidden layer size, 3 relative actions
        self.model = Linear_QNet(14, 256, 128, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def remember(self, state, action, reward, next_state, done):
        """Stores an experience tuple in the replay memory buffer."""
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        """
        Samples a mini-batch from experience memory and performs a training step.
        Crucial for stabilizing DQN learning.
        """
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        """Trains on the single transition that just occurred."""
        self.trainer.train_step(state, action, reward, next_state, done)

    def train_replay_batch(self, batch_size: int = REPLAY_BATCH_SIZE):
        """Trains on a small random mini-batch from replay memory (decorrelated, batched)."""
        if len(self.memory) < batch_size:
            return
        states, actions, rewards, next_states, dones = zip(*random.sample(self.memory, batch_size))
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def get_action(self, state: list[float]) -> tuple[list[int], torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """
        Decides an action using the epsilon-greedy strategy.
        Returns:
            final_move: one-hot action [straight, right, left]
            prediction: Q-values tensor
            hidden_activations: (hidden1, hidden2) tensors
        """
        final_move = [0, 0, 0]

        state_tensor = torch.tensor(state, dtype=torch.float)
        prediction, hidden_activations = self.model.forward_with_activations(state_tensor)

        # Exploration vs Exploitation
        if random.random() < self.epsilon:
            move_idx = random.randint(0, 2)
            final_move[move_idx] = 1
        else:
            move_idx = torch.argmax(prediction).item()
            final_move[move_idx] = 1

        return final_move, prediction, hidden_activations


def train_visual(fps: int = 40):
    """
    Runs the AI training loop accompanied by real-time Pygame visualization
    of both the Snake game board and the neural network activations.
    Press 'F' or 'SPACE' to toggle Fast (Turbo) Training Mode.
    """
    agent = Agent()
    env = Environment()

    cell_size = 20
    game_width = env.cols * cell_size
    game_height = env.rows * cell_size
    network_panel_width = 540
    screen_width = game_width + network_panel_width
    screen_height = max(game_height, 480)

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Snake AI - Neural Network Live Activation (Press F for Turbo)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)

    visualizer = NeuralVisualizer(start_x=game_width, start_y=0, width=network_panel_width, height=screen_height)

    record = 0
    total_score = 0
    running = True
    fast_mode = False  # Toggle with 'F' or 'SPACE'
    total_steps = 0
    state_old = env.get_state()  # Computed once; afterwards reused from env.step()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_f, pygame.K_SPACE):
                    fast_mode = not fast_mode
                    print(f"--- Fast Turbo Mode: {'ON (Max Speed)' if fast_mode else 'OFF (Visual Mode)'} ---")

        # 1. Pick action with neural network activations (state_old carried over from the previous step)
        final_move, q_values, hidden_acts = agent.get_action(state_old)

        # 2. Advance game environment
        state_new, reward, done, score = env.step(final_move)

        # 3. Store experience and train on a replay mini-batch every TRAIN_EVERY steps
        agent.remember(state_old, final_move, reward, state_new, done)
        total_steps += 1
        if total_steps % TRAIN_EVERY == 0:
            agent.train_replay_batch()

        # ---------------------------------------------------------------------
        # Rendering (Skipped during Fast Mode for maximum training speed)
        # ---------------------------------------------------------------------
        if not fast_mode:
            screen.fill((10, 12, 16))

            # Draw grid & cells
            for r in range(env.rows):
                for c in range(env.cols):
                    cell = env.game_area[r][c]
                    px = c * cell_size
                    py = r * cell_size

                    if cell == CellState.SNAKE:
                        color = (0, 255, 120)
                    elif cell == CellState.FOOD:
                        color = (255, 65, 80)
                    else:
                        color = (20, 24, 30)

                    pygame.draw.rect(screen, color, (px, py, cell_size - 1, cell_size - 1))

            # Draw UI overlay
            ui_text = font.render(f"Game: {agent.n_games} | Score: {score} | Record: {record} | [F/Space] Turbo: OFF", True, (255, 255, 255))
            screen.blit(ui_text, (15, 12))

            # Draw live Neural Network schematic
            visualizer.draw(screen, state_old, hidden_acts, q_values, final_move)

            pygame.display.flip()
            clock.tick(fps)

        state_old = state_new

        if done:
            env.reset_environment()
            state_old = env.get_state()  # fresh state for the new game
            agent.n_games += 1
            agent.train_long_memory()
            agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)

            if score > record:
                record = score
                agent.model.save()

            total_score += score
            mean_score = total_score / agent.n_games
            print(f"Game: {agent.n_games} | Score: {score} | Record: {record} | Mean: {mean_score:.2f} | Epsilon: {agent.epsilon:.3f}")

            # Even in fast mode, update the window title occasionally so you know the progress
            if fast_mode and agent.n_games % 10 == 0:
                pygame.display.set_caption(f"TURBO MODE - Game: {agent.n_games} | Record: {record} | Mean: {mean_score:.2f} (Press F)")

    pygame.quit()


if __name__ == "__main__":
    train_visual(fps=40)
