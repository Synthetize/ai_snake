import pygame
import torch

INPUT_LABELS = [
    "Danger Straight",
    "Danger Right",
    "Danger Left",
    "Moving UP",
    "Moving RIGHT",
    "Moving DOWN",
    "Moving LEFT",
    "Food UP",
    "Food DOWN",
    "Food LEFT",
    "Food RIGHT",
    "Space Straight",
    "Space Right",
    "Space Left",
]

OUTPUT_LABELS = [
    "Straight",
    "Turn Right",
    "Turn Left",
]


class NeuralVisualizer:
    """
    Renders a live schematic of the complete deep neural network:
    Input features (14), Hidden Layer 1, Hidden Layer 2, and Output Q-values with chosen action.
    """

    def __init__(self, start_x: int, start_y: int, width: int, height: int):
        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = height

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 11)
        self.title_font = pygame.font.SysFont("Arial", 15, bold=True)
        self.layer_header_font = pygame.font.SysFont("Arial", 11, bold=True)
        self.q_font = pygame.font.SysFont("Arial", 12, bold=True)

        self.num_inputs = 14
        self.num_hidden1_displayed = 14
        self.num_hidden2_displayed = 10
        self.num_outputs = 3

    def draw(self, surface: pygame.Surface, state: list[float], hidden_activations: tuple[torch.Tensor, torch.Tensor], q_values: torch.Tensor, chosen_action: list[int]):
        """Draws all 4 layers and their synaptic connections."""
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (18, 22, 28), panel_rect)
        pygame.draw.line(surface, (55, 65, 80), (self.x, self.y), (self.x, self.y + self.height), 2)

        # Title
        title = self.title_font.render("Deep Q-Network (14 -> 256 -> 128 -> 3)", True, (220, 230, 245))
        surface.blit(title, (self.x + 18, self.y + 12))

        # Layer X-coordinates
        x_input = self.x + 115
        x_h1 = self.x + 215
        x_h2 = self.x + 305
        x_output = self.x + 395

        # Layer Headers
        surface.blit(self.layer_header_font.render("Input", True, (140, 155, 175)), (x_input - 15, 38))
        surface.blit(self.layer_header_font.render("H1 (256)", True, (140, 155, 175)), (x_h1 - 20, 38))
        surface.blit(self.layer_header_font.render("H2 (128)", True, (140, 155, 175)), (x_h2 - 20, 38))
        surface.blit(self.layer_header_font.render("Output", True, (140, 155, 175)), (x_output - 15, 38))

        # Positions
        input_positions = self._get_positions(x_input, self.num_inputs, y_start=60, y_end=self.height - 25)
        h1_positions = self._get_positions(x_h1, self.num_hidden1_displayed, y_start=60, y_end=self.height - 25)
        h2_positions = self._get_positions(x_h2, self.num_hidden2_displayed, y_start=85, y_end=self.height - 50)
        output_positions = self._get_positions(x_output, self.num_outputs, y_start=140, y_end=self.height - 140)

        # ---------------------------------------------------------------------
        # Synaptic Connections (light lines)
        # ---------------------------------------------------------------------
        for i_pos in input_positions:
            for h1_pos in h1_positions[::2]:
                pygame.draw.line(surface, (30, 38, 50), i_pos, h1_pos, 1)

        for h1_pos in h1_positions:
            for h2_pos in h2_positions[::2]:
                pygame.draw.line(surface, (38, 46, 60), h1_pos, h2_pos, 1)

        for h2_pos in h2_positions:
            for o_pos in output_positions:
                pygame.draw.line(surface, (45, 55, 75), h2_pos, o_pos, 1)

        # ---------------------------------------------------------------------
        # 1. Input Layer
        # ---------------------------------------------------------------------
        for idx, (pos_x, pos_y) in enumerate(input_positions):
            val = float(state[idx]) if idx < len(state) else 0.0

            # Last 3 inputs are continuous values [0.0 - 1.0] (reachable space)
            if idx >= 11:
                intensity = int(min(255, max(0, val * 255)))
                color = (0, intensity, int(intensity * 0.8) + 40)
                radius = 6
                label_text = f"{INPUT_LABELS[idx]} ({int(val * 100)}%)"
            else:
                is_active = bool(val)
                color = (0, 230, 140) if is_active else (45, 55, 70)
                radius = 6 if is_active else 4
                label_text = INPUT_LABELS[idx]

            pygame.draw.circle(surface, color, (pos_x, pos_y), radius)

            label = self.font.render(label_text, True, (180, 195, 215) if val > 0 else (90, 105, 120))
            text_rect = label.get_rect(right=pos_x - 10, centery=pos_y)
            surface.blit(label, text_rect)

        # ---------------------------------------------------------------------
        # 2. Hidden Layer 1 (256 neurons, sampled)
        # ---------------------------------------------------------------------
        h1_acts, h2_acts = hidden_activations if hidden_activations is not None else (None, None)

        if h1_acts is not None:
            acts1 = h1_acts.squeeze().detach().cpu()
            max_act1 = torch.max(acts1).item() if torch.max(acts1) > 0 else 1.0

            for idx, (pos_x, pos_y) in enumerate(h1_positions):
                val = acts1[idx * 18].item() if idx * 18 < len(acts1) else 0.0
                intensity = int(min(255, max(0, (val / max_act1) * 255)))
                color = (intensity, int(intensity * 0.6), 255)
                pygame.draw.circle(surface, color, (pos_x, pos_y), 5)
        else:
            for pos_x, pos_y in h1_positions:
                pygame.draw.circle(surface, (50, 60, 75), (pos_x, pos_y), 5)

        # ---------------------------------------------------------------------
        # 3. Hidden Layer 2 (128 neurons, sampled)
        # ---------------------------------------------------------------------
        if h2_acts is not None:
            acts2 = h2_acts.squeeze().detach().cpu()
            max_act2 = torch.max(acts2).item() if torch.max(acts2) > 0 else 1.0

            for idx, (pos_x, pos_y) in enumerate(h2_positions):
                val = acts2[idx * 12].item() if idx * 12 < len(acts2) else 0.0
                intensity = int(min(255, max(0, (val / max_act2) * 255)))
                color = (int(intensity * 0.8), 120, intensity)
                pygame.draw.circle(surface, color, (pos_x, pos_y), 5)
        else:
            for pos_x, pos_y in h2_positions:
                pygame.draw.circle(surface, (50, 60, 75), (pos_x, pos_y), 5)

        # ---------------------------------------------------------------------
        # 4. Output Layer
        # ---------------------------------------------------------------------
        chosen_idx = chosen_action.index(1) if 1 in chosen_action else 0
        q_vals = q_values.squeeze().detach().cpu().numpy() if q_values is not None else [0.0, 0.0, 0.0]

        for idx, (pos_x, pos_y) in enumerate(output_positions):
            is_chosen = (idx == chosen_idx)
            color = (255, 185, 30) if is_chosen else (65, 80, 105)
            radius = 10 if is_chosen else 7

            pygame.draw.circle(surface, color, (pos_x, pos_y), radius)
            if is_chosen:
                pygame.draw.circle(surface, (255, 255, 255), (pos_x, pos_y), radius + 2, 2)

            q_text = f"{OUTPUT_LABELS[idx]}  (Q={q_vals[idx]:.2f})"
            label = self.q_font.render(q_text, True, (255, 220, 100) if is_chosen else (145, 160, 180))
            surface.blit(label, (pos_x + 15, pos_y - 7))

    def _get_positions(self, x: int, count: int, y_start: int, y_end: int) -> list[tuple[int, int]]:
        """Distributes neuron centers evenly along a vertical column."""
        step = (y_end - y_start) / max(1, count - 1)
        return [(x, int(y_start + i * step)) for i in range(count)]
