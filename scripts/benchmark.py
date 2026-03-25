#!/usr/bin/env python3
# Benchmark the saved best bot against two baselines:
#   1. Random bot          — measures absolute strength
#   2. Default-weights minimax — measures improvement from training
#
# Usage:
#   python3 scripts/benchmark.py
#   python3 scripts/benchmark.py --games 200 --depth 6 --workers 5
#
# NOTE: the if __name__ == '__main__' guard is required when using
# multiprocessing — without it, worker processes would re-execute this
# script and spawn infinitely.
import sys
import time
import argparse
import multiprocessing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.runner import run_games
from src.bots.minimax import make_minimax_bot, DEFAULT_WEIGHTS
from src.bots.random import random_bot
from src.io.persistence import load_best
from src.viz.metrics import fmt_weights


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _print_result(label, result, total):
    wins   = result['wins']
    losses = result['losses']
    draws  = result['draws']
    def pct(n): return f'{n / total * 100:.1f}%'.rjust(6)
    print('')
    print(f'  {label}')
    print(f'    Wins   {wins:4d}   / {total}  ({pct(wins)})')
    print(f'    Losses {losses:4d} / {total}  ({pct(losses)})')
    print(f'    Draws  {draws:4d}  / {total}  ({pct(draws)})')
    print('')


def main():
    # ─── Config ───────────────────────────────────────────────────────────────

    parser = argparse.ArgumentParser(description='Benchmark trained bot vs baselines.')
    parser.add_argument('--games',   type=int, default=200,
                        help='Games per matchup (default: 200)')
    parser.add_argument('--depth',   type=int, default=6,
                        help='Search depth (default: 6)')
    parser.add_argument('--workers', type=int, default=5,
                        help='Parallel worker processes (default: 5)')
    args = parser.parse_args()

    cfg = {'games': args.games, 'depth': args.depth, 'workers': args.workers}

    # ─── Load best bot ────────────────────────────────────────────────────────

    seed = load_best(DEFAULT_WEIGHTS)

    if seed['generation'] == 0:
        print('No trained weights found. Run train.py first.', file=sys.stderr)
        sys.exit(1)

    print('Connect4 AI — Benchmark')
    print('─' * 60)
    print(f"  Loaded: gen {seed['generation']}  fitness {seed['fitness']:.4f}")
    print(f"  Weights: {fmt_weights(seed['weights'])}")
    print(f"  Games per matchup: {cfg['games']}  |  Search depth: {cfg['depth']}"
          f"  |  Workers: {cfg['workers']}")
    print('─' * 60)
    print('')

    best_bot    = make_minimax_bot(cfg['depth'], seed['weights'])
    default_bot = make_minimax_bot(cfg['depth'], DEFAULT_WEIGHTS)

    # ─── vs Random ───────────────────────────────────────────────────────────

    print(f"Running {cfg['games']} games vs random bot ...", end='', flush=True)
    start1    = time.perf_counter()
    vs_random = run_games(best_bot, random_bot, cfg['games'])
    t1        = time.perf_counter() - start1
    print(f'  done ({t1:.1f}s)')
    _print_result('Best bot vs Random', vs_random, cfg['games'])

    # ─── vs Default weights ───────────────────────────────────────────────────

    print(f"Running {cfg['games']} games vs default-weights minimax ...", end='', flush=True)
    start2     = time.perf_counter()
    vs_default = run_games(best_bot, default_bot, cfg['games'])
    t2         = time.perf_counter() - start2
    print(f'  done ({t2:.1f}s)')
    _print_result(f"Best bot vs Default (depth {cfg['depth']})", vs_default, cfg['games'])

    # ─── Summary ─────────────────────────────────────────────────────────────

    print('─' * 60)
    total_wins   = vs_random['wins'] + vs_default['wins']
    overall_rate = total_wins / (cfg['games'] * 2)
    print(f'Overall win rate: {overall_rate * 100:.1f}%  '
          f'({total_wins}W / {cfg["games"] * 2} games)')
    print('')


if __name__ == '__main__':
    multiprocessing.set_start_method('fork')
    main()
