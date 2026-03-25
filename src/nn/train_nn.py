"""
train_nn.py — Training loop for the Phase B neural network.

Loop structure (per iteration):
  1. Self-play  : candidate network generates games → push to replay buffer
  2. Train step : sample buffer, gradient descent on MSE loss
  3. Evaluate   : every eval_every iters, candidate vs champion (50 games)
                  if win_rate > 0.55 → candidate becomes new champion
  4. Checkpoint : every 10 iters → models/checkpoint_NNN.pt
"""
import copy
from pathlib import Path

import torch
import torch.nn as nn

from ..nn.network   import Connect4Net
from ..nn.replay    import ReplayBuffer
from ..nn.self_play import generate_games, make_nn_mcts_bot
from ..simulation.runner import run_games

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT       = Path(__file__).parents[2]
_MODELS_DIR = _ROOT / "models"
_BEST_PATH  = _MODELS_DIR / "best_model.pt"


# ---------------------------------------------------------------------------
# Core training primitives
# ---------------------------------------------------------------------------

def train_step(network, optimiser, buffer, batch_size, device):
    """
    One gradient-descent step.

    Parameters
    ----------
    network    : Connect4Net in train() mode
    optimiser  : torch.optim.Optimizer
    buffer     : ReplayBuffer
    batch_size : int
    device     : torch.device

    Returns
    -------
    float — scalar MSE loss for this step
    """
    states, outcomes = buffer.sample(batch_size)
    states   = states.to(device)
    outcomes = outcomes.to(device)

    optimiser.zero_grad()
    predictions = network(states)               # (B, 1)
    loss = nn.functional.mse_loss(predictions, outcomes)
    loss.backward()
    optimiser.step()

    return loss.item()


def evaluate(new_net, champion_net, device, n_games=50, iterations=200):
    """
    Play `n_games` games between `new_net` and `champion_net` using
    network-backed MCTS bots (alternating first player).

    Parameters
    ----------
    new_net      : Connect4Net
    champion_net : Connect4Net
    device       : torch.device
    n_games      : int
    iterations   : int — MCTS iterations per move during evaluation

    Returns
    -------
    float — win rate of new_net (wins / n_games)
    """
    new_net.eval()
    champion_net.eval()

    bot_new      = make_nn_mcts_bot(new_net,      device, iterations=iterations)
    bot_champion = make_nn_mcts_bot(champion_net, device, iterations=iterations)

    result = run_games(bot_new, bot_champion, n_games)
    return result['wins'] / n_games


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def training_loop(opts):
    """
    Run the full self-play → train → evaluate loop.

    Parameters
    ----------
    opts : argparse.Namespace with attributes:
        iterations   int   total training iterations
        games        int   self-play games per iteration
        mcts_iters   int   MCTS iterations per move during self-play
        batch_size   int   gradient step batch size
        train_steps  int   gradient steps per iteration
        eval_every   int   evaluate vs champion every N iterations
    """
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    _MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Initialise champion ──────────────────────────────────────────────────
    if _BEST_PATH.exists():
        print(f"Loading champion from {_BEST_PATH}")
        champion = Connect4Net.load(_BEST_PATH, device)
    else:
        print("No saved champion — starting from scratch")
        champion = Connect4Net().to(device)
        champion.eval()

    # ── Initialise candidate as a deep copy of champion ──────────────────────
    candidate = copy.deepcopy(champion).to(device)
    optimiser = torch.optim.Adam(candidate.parameters(), lr=1e-3)
    buffer    = ReplayBuffer()

    print(f"Training on device: {device}")
    print(f"Iterations={opts.iterations}  games/iter={opts.games}  "
          f"mcts_iters={opts.mcts_iters}  batch={opts.batch_size}  "
          f"train_steps={opts.train_steps}  eval_every={opts.eval_every}\n")

    for i in range(1, opts.iterations + 1):

        # ── a. Self-play ─────────────────────────────────────────────────────
        champion.eval()
        candidate.eval()
        samples = generate_games(candidate, device, opts.games, opts.mcts_iters)
        for tensor, outcome in samples:
            buffer.push(tensor, outcome)

        # ── b. Train ─────────────────────────────────────────────────────────
        loss_val = None
        if len(buffer) >= opts.batch_size:
            candidate.train()
            for _ in range(opts.train_steps):
                loss_val = train_step(candidate, optimiser, buffer,
                                      opts.batch_size, device)
            candidate.eval()

        loss_str = f"{loss_val:.4f}" if loss_val is not None else "n/a (buffer too small)"
        print(f"Iter {i:4d}/{opts.iterations}  loss={loss_str}  buffer={len(buffer)}")

        # ── c. Evaluate ──────────────────────────────────────────────────────
        if i % opts.eval_every == 0:
            win_rate = evaluate(candidate, champion, device,
                                n_games=50, iterations=opts.mcts_iters)
            promoted = win_rate > 0.55
            print(f"  ↳ Eval (iter {i}): candidate win rate = {win_rate:.3f} "
                  f"{'→ NEW CHAMPION saved' if promoted else '(champion retained)'}")
            if promoted:
                champion = copy.deepcopy(candidate).to(device)
                champion.eval()
                champion.save(_BEST_PATH)

        # ── d. Checkpoint every 10 iterations ────────────────────────────────
        if i % 10 == 0:
            ckpt = _MODELS_DIR / f"checkpoint_{i:03d}.pt"
            candidate.save(ckpt)
            print(f"  ↳ Checkpoint saved: {ckpt.name}")

    print("\nTraining complete.")
