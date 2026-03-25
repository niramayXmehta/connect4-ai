"""
replay.py — Experience replay buffer for neural network training.

Stores (state_tensor, outcome) pairs. When full, the oldest entry is dropped
(deque with maxlen). Outcomes are floats from the player-to-move's perspective:
  +1.0  win
  -1.0  loss
   0.0  draw
"""
import random
from collections import deque
import torch


class ReplayBuffer:
    """Circular buffer of (state_tensor, outcome) pairs."""

    def __init__(self, capacity=50_000):
        self._buf = deque(maxlen=capacity)

    def push(self, state_tensor, outcome):
        """
        Store one training sample.

        Parameters
        ----------
        state_tensor : torch.Tensor of shape (3, ROWS, COLS)
        outcome      : float — +1.0 / -1.0 / 0.0
        """
        self._buf.append((state_tensor, float(outcome)))

    def sample(self, batch_size):
        """
        Draw `batch_size` samples uniformly at random (with replacement if
        the buffer is smaller than batch_size).

        Returns
        -------
        states   : torch.Tensor  shape (B, 3, ROWS, COLS), float32
        outcomes : torch.Tensor  shape (B, 1),              float32
        """
        batch = random.choices(self._buf, k=batch_size)
        states, outcomes = zip(*batch)
        return (
            torch.stack(states).float(),
            torch.tensor(outcomes, dtype=torch.float32).unsqueeze(1),
        )

    def __len__(self):
        return len(self._buf)
