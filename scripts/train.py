#!/usr/bin/env python3
# CLI entry point: run the Phase A evolutionary training loop.
#
# Usage:
#   python scripts/train.py
#   python scripts/train.py --gens 50 --pop 20 --depth 4 --games 20 --elite 4
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.evolution import evolve

parser = argparse.ArgumentParser(description='Phase A evolutionary weight tuning.')
parser.add_argument('--gens',   type=int, help='Number of generations')
parser.add_argument('--pop',    type=int, help='Population size')
parser.add_argument('--depth',  type=int, help='Search depth')
parser.add_argument('--games',  type=int, help='Games per matchup')
parser.add_argument('--elite',  type=int, help='Elite count')
args = parser.parse_args()

opts = {}
if args.gens  is not None: opts['generations']      = args.gens
if args.pop   is not None: opts['population_size']  = args.pop
if args.depth is not None: opts['search_depth']     = args.depth
if args.games is not None: opts['games_per_matchup']= args.games
if args.elite is not None: opts['elite_count']      = args.elite

evolve(opts)
