#!/usr/bin/env node
// CLI: simulate N games between minimax (depth 4) and the random bot.
// Usage: node scripts/simulate.js [N]
import { runGames } from '../src/simulation/runner.js';
import { makeMinimaxBot } from '../src/bots/minimax.js';
import { randomBot } from '../src/bots/random.js';

const N = parseInt(process.argv[2] ?? '100', 10);
if (isNaN(N) || N < 1) {
  console.error('Usage: node scripts/simulate.js [N]   (N = number of games, default 100)');
  process.exit(1);
}

const minimax = makeMinimaxBot(4); // depth 4 per Phase A training spec

console.log(`\nSimulating ${N} games: minimax (depth 4) vs random — alternating first player\n`);
const start = Date.now();
const { wins, losses, draws } = runGames(minimax, randomBot, N);
const elapsed = ((Date.now() - start) / 1000).toFixed(2);

const pct = (n) => ((n / N) * 100).toFixed(1);

console.log(`Results (minimax perspective):`);
console.log(`  Wins:   ${String(wins).padStart(4)}  (${pct(wins)}%)`);
console.log(`  Losses: ${String(losses).padStart(4)}  (${pct(losses)}%)`);
console.log(`  Draws:  ${String(draws).padStart(4)}  (${pct(draws)}%)`);
console.log(`  Total:  ${N} games in ${elapsed}s`);
