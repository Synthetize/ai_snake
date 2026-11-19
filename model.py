import copy
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class Linear_QNet(nn.Module):
    """
    Feed-Forward Neural Network (Multi-Layer Perceptron) for Q-Learning.
    Maps a 14-feature state vector to Q-values for 3 relative actions
    through two deep hidden layers: 14 -> 256 -> 128 -> 3.
    """

    def __init__(self, input_size: int = 14, hidden_size: int = 256, hidden_size2: int = 128, output_size: int = 3):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size2)
        self.linear3 = nn.Linear(hidden_size2, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network with ReLU activations."""
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        return self.linear3(x)

    def forward_with_activations(self, x: torch.Tensor) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """
        Returns the final Q-values and activations for BOTH hidden layers
        for comprehensive real-time neural visualization.
        """
        hidden1 = F.relu(self.linear1(x))
        hidden2 = F.relu(self.linear2(hidden1))
        output = self.linear3(hidden2)
        return output, (hidden1, hidden2)

    def save(self, file_name: str = "model.pth"):
        """Saves network weights to a checkpoint file."""
        model_folder_path = "./model"
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_path = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_path)


class QTrainer:
    """
    Handles optimization and loss computation via Bellman Equation and Adam optimizer.
    Uses a frozen target network (periodically synced) to compute the Bellman target,
    so the network is not chasing a target that moves at every gradient step.
    """

    def __init__(self, model: Linear_QNet, lr: float = 0.001, gamma: float = 0.9, target_update_every: int = 500):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

        self.target_model = copy.deepcopy(model)
        self.target_model.eval()
        for param in self.target_model.parameters():
            param.requires_grad_(False)
        self.target_update_every = target_update_every
        self.train_steps = 0

    def sync_target(self):
        """Copies the online network weights into the frozen target network."""
        self.target_model.load_state_dict(self.model.state_dict())

    def train_step(self, state, action, reward, next_state, done):
        """
        Executes one optimization step on a single experience or a mini-batch.
        Uses Bellman's equation: Q_new = Reward + gamma * max(Q_target(next_state))
        """
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)
        done = torch.tensor(np.array(done), dtype=torch.bool)

        if state.dim() == 1:
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = reward.unsqueeze(0)
            done = done.unsqueeze(0)

        pred = self.model(state)

        with torch.no_grad():
            next_q_max = self.target_model(next_state).max(dim=1).values
            q_new = reward + self.gamma * next_q_max * (~done).float()

        target = pred.detach().clone()
        action_idx = action.argmax(dim=1)
        target[torch.arange(len(action_idx)), action_idx] = q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()

        self.train_steps += 1
        if self.train_steps % self.target_update_every == 0:
            self.sync_target()
