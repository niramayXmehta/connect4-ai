#!/usr/bin/env python3
# CLI: simulate N games between various bot matchups.
# Usage: python scripts/simulate.py [--mode MODE] [--games N] [--iterations I] [--rollout POLICY]
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.runner import run_games
from src.bots.minimax import make_minimax_bot, DEFAULT_WEIGHTS
from src.bots.mcts import make_mcts_bot
from src.bots.random import random_bot
from src.io.persistence import load_best

import argparse

MODES = ['minimax_vs_random', 'mcts_vs_random', 'mcts_vs_minimax', 'minimax_vs_mcts']

parser = argparse.ArgumentParser(description='Simulate N games between two bots.')
parser.add_argument('--mode', choices=MODES, default='minimax_vs_random',
                    help='Matchup mode (default: minimax_vs_random)')
parser.add_argument('--games', type=int, default=100,
                    help='Number of games (default: 100)')
parser.add_argument('--iterations', type=int, default=500,
                    help='MCTS iterations per move (default: 500)')
parser.add_argument('--rollout', choices=['random', 'weighted'], default='random',
                    help='MCTS rollout policy: random (default) or weighted (uses best.json weights)')
parser.add_argument('--temperature', type=float, default=1.0,
                    help='Softmax temperature for weighted rollout (default 1.0). '
                         'Higher = more random, lower = more greedy. Ignored when --rollout random.')
# Legacy positional arg kept for backwards compatibility
parser.add_argument('N', nargs='?', type=int, default=None,
                    help='[deprecated] Number of games — use --games instead')
args = parser.parse_args()

N = args.N if args.N is not None else args.games
if N < 1:
    parser.error('N must be a positive integer')

mode        = args.mode
iterations  = args.iterations
rollout     = args.rollout
temperature = args.temperature

# Resolve rollout weights when the weighted policy is requested.
rollout_weights = None
rollout_label   = 'random rollout'
if rollout == 'weighted':
    saved = load_best(DEFAULT_WEIGHTS)
    rollout_weights = saved['weights']
    gen             = saved['generation']
    fitness         = saved['fitness']
    rollout_label   = f'weighted rollout T={temperature} (gen {gen}, fitness {fitness:.3f})'

# Build bots
minimax = make_minimax_bot(4)
mcts    = make_mcts_bot(iterations=iterations, rollout_weights=rollout_weights,
                        temperature=temperature)

mcts_name = f'mcts ({iterations} iters, {rollout_label})'

BOT_CONFIGS = {
    'minimax_vs_random': (minimax, random_bot, 'minimax (depth 4)', 'random'),
    'mcts_vs_random':    (mcts,    random_bot, mcts_name,           'random'),
    'mcts_vs_minimax':   (mcts,    minimax,    mcts_name,           'minimax (depth 4)'),
    'minimax_vs_mcts':   (minimax, mcts,       'minimax (depth 4)', mcts_name),
}

bot_a, bot_b, name_a, name_b = BOT_CONFIGS[mode]

print(f'\nSimulating {N} games: {name_a} vs {name_b} — alternating first player\n')
start = time.perf_counter()
result = run_games(bot_a, bot_b, N)
elapsed = time.perf_counter() - start

wins   = result['wins']
losses = result['losses']
draws  = result['draws']

def pct(n):
    return f'{n / N * 100:.1f}%'

print(f'Results ({name_a} perspective):')
print(f'  Wins:   {wins:4d}  ({pct(wins)})')
print(f'  Losses: {losses:4d}  ({pct(losses)})')
print(f'  Draws:  {draws:4d}  ({pct(draws)})')
print(f'  Total:  {N} games in {elapsed:.2f}s  ({elapsed/N*1000:.0f} ms/game)')
