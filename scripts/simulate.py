#!/usr/bin/env python3
# CLI: simulate N games between minimax (depth 4) and the random bot.
# Usage: python scripts/simulate.py [N]
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.runner import run_games
from src.bots.minimax import make_minimax_bot
from src.bots.random import random_bot

import argparse

parser = argparse.ArgumentParser(description='Simulate N games: minimax vs random.')
parser.add_argument('N', nargs='?', type=int, default=100,
                    help='Number of games (default: 100)')
args = parser.parse_args()

N = args.N
if N < 1:
    parser.error('N must be a positive integer')

minimax = make_minimax_bot(4)  # depth 4 per Phase A training spec

print(f'\nSimulating {N} games: minimax (depth 4) vs random — alternating first player\n')
start = time.perf_counter()
result = run_games(minimax, random_bot, N)
elapsed = time.perf_counter() - start

wins   = result['wins']
losses = result['losses']
draws  = result['draws']

def pct(n):
    return f'{n / N * 100:.1f}%'

print('Results (minimax perspective):')
print(f'  Wins:   {wins:4d}  ({pct(wins)})')
print(f'  Losses: {losses:4d}  ({pct(losses)})')
print(f'  Draws:  {draws:4d}  ({pct(draws)})')
print(f'  Total:  {N} games in {elapsed:.2f}s')
