#!/usr/bin/env python3
# CLI entry point: run the Phase A evolutionary training loop.
#
# Usage:
#   python3 scripts/train.py
#   python3 scripts/train.py --gens 50 --pop 20 --depth 4 --games 20 --elite 4
#   python3 scripts/train.py --gens 3 --pop 20 --games 20 --elite 4 --workers 5
#
# NOTE: the if __name__ == '__main__' guard is required when using
# multiprocessing — without it, worker processes would re-execute this
# script and spawn infinitely (especially on macOS with spawn/fork).
import sys
import argparse
import multiprocessing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.evolution import evolve


def main():
    parser = argparse.ArgumentParser(description='Phase A evolutionary weight tuning.')
    parser.add_argument('--gens',    type=int, help='Number of generations')
    parser.add_argument('--pop',     type=int, help='Population size')
    parser.add_argument('--depth',   type=int, help='Search depth')
    parser.add_argument('--games',   type=int, help='Games per matchup')
    parser.add_argument('--elite',   type=int, help='Elite count')
    parser.add_argument('--workers', type=int, default=5,
                        help='Parallel worker processes (default: 5, use 1 for sequential)')
    args = parser.parse_args()

    opts = {}
    if args.gens    is not None: opts['generations']       = args.gens
    if args.pop     is not None: opts['population_size']   = args.pop
    if args.depth   is not None: opts['search_depth']      = args.depth
    if args.games   is not None: opts['games_per_matchup'] = args.games
    if args.elite   is not None: opts['elite_count']       = args.elite
    opts['workers'] = args.workers

    evolve(opts)


if __name__ == '__main__':
    # fork inherits the parent's imported modules and sys.path — no re-import
    # needed in workers.  spawn (macOS default) would require workers to
    # re-import src.*, which needs the project root in sys.path; fork avoids
    # that complexity entirely for this pure-Python CPU workload.
    multiprocessing.set_start_method('fork')
    main()
