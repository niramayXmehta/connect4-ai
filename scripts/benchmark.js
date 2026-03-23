#!/usr/bin/env node
// CLI entry point: test the current best bot against random and baseline bots.
import { runGames } from '../src/simulation/runner.js';
import { minimaxBot } from '../src/bots/minimax.js';
import { randomBot } from '../src/bots/random.js';
import { readFileSync } from 'node:fs';

const bestWeights = JSON.parse(
  readFileSync(new URL('../data/weights/best.json', import.meta.url)),
);

const N = 200;
console.log(`Benchmarking best bot (gen ${bestWeights.generation}) over ${N} games each...\n`);

// TODO: print formatted table of results
const vsRandom = runGames(
  (board) => minimaxBot(board, 6, bestWeights.weights),
  (board) => randomBot(board),
  N,
);
console.log('vs random:', vsRandom);
