#!/usr/bin/python3
"""
scripts/train_nn.py — CLI entry point for Phase B neural network training.

Usage examples:
  python3 scripts/train_nn.py                            # defaults
  python3 scripts/train_nn.py --iterations 200 --games 20
  python3 scripts/train_nn.py --iterations 3 --games 5 --mcts-iters 30 \
      --batch-size 32 --train-steps 8 --eval-every 3   # sanity check
"""
import sys
import argparse
from pathlib import Path

# Make the project root importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nn.train_nn import training_loop


def _parse_args():
    p = argparse.ArgumentParser(
        description="Train the Phase B Connect4 neural network via self-play MCTS."
    )
    p.add_argument("--iterations",   type=int, default=100,
                   help="Total training iterations (default: 100)")
    p.add_argument("--games",        type=int, default=50,
                   help="Self-play games per iteration (default: 50)")
    p.add_argument("--mcts-iters",   type=int, default=200, dest="mcts_iters",
                   help="MCTS iterations per move (default: 200)")
    p.add_argument("--batch-size",   type=int, default=256, dest="batch_size",
                   help="Training batch size (default: 256)")
    p.add_argument("--train-steps",  type=int, default=64,  dest="train_steps",
                   help="Gradient steps per iteration (default: 64)")
    p.add_argument("--eval-every",        type=int, default=10,  dest="eval_every",
                   help="Evaluate vs champion every N iterations (default: 10)")
    p.add_argument("--checkpoint-every", type=int, default=10,  dest="checkpoint_every",
                   help="Save checkpoint every N iterations (default: 10)")
    return p.parse_args()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method("fork")

    opts = _parse_args()
    training_loop(opts)
