#!/usr/bin/env node
// CLI entry point: simulate N games between two saved bots and print a summary.
import { runGames } from '../src/simulation/runner.js';
import { minimaxBot } from '../src/bots/minimax.js';
import { randomBot } from '../src/bots/random.js';

const N = parseInt(process.argv[2] ?? '100', 10);

console.log(`Simulating ${N} games: minimax vs random...`);
// TODO: load bots from data/weights/ based on CLI args
const results = runGames(
  (board, token) => minimaxBot(board, 6),
  (board, token) => randomBot(board),
  N,
);
console.log(results);
