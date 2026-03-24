#!/usr/bin/env node
// Benchmark the saved best bot against two baselines:
//   1. Random bot       — measures absolute strength
//   2. Default-weights minimax — measures improvement from training
//
// Usage:
//   node scripts/benchmark.js
//   node scripts/benchmark.js --games 200 --depth 6
import { runGames }                        from '../src/simulation/runner.js';
import { makeMinimaxBot, DEFAULT_WEIGHTS } from '../src/bots/minimax.js';
import { randomBot }                       from '../src/bots/random.js';
import { loadBest }                        from '../src/io/persistence.js';
import { fmtWeights }                      from '../src/viz/metrics.js';

// ─── Config ───────────────────────────────────────────────────────────────────

const DEFAULTS = { games: 200, depth: 6 };

const cfg = parseArgs(process.argv);

// ─── Load best bot ────────────────────────────────────────────────────────────

const seed = loadBest(DEFAULT_WEIGHTS);

if (seed.generation === 0) {
  console.error('No trained weights found. Run train.js first.');
  process.exit(1);
}

console.log('Connect4 AI — Benchmark');
console.log('─'.repeat(60));
console.log(`  Loaded: gen ${seed.generation}  fitness ${seed.fitness.toFixed(4)}`);
console.log(`  Weights: ${fmtWeights(seed.weights)}`);
console.log(`  Games per matchup: ${cfg.games}  |  Search depth: ${cfg.depth}`);
console.log('─'.repeat(60));
console.log('');

const bestBot    = makeMinimaxBot(cfg.depth, seed.weights);
const defaultBot = makeMinimaxBot(cfg.depth, DEFAULT_WEIGHTS);

// ─── vs Random ───────────────────────────────────────────────────────────────

process.stdout.write(`Running ${cfg.games} games vs random bot ...`);
const start1   = Date.now();
const vsRandom = runGames(bestBot, randomBot, cfg.games);
const t1       = ((Date.now() - start1) / 1000).toFixed(1);
process.stdout.write(`  done (${t1}s)\n`);
printResult('Best bot vs Random', vsRandom, cfg.games);

// ─── vs Default weights ───────────────────────────────────────────────────────

process.stdout.write(`Running ${cfg.games} games vs default-weights minimax ...`);
const start2    = Date.now();
const vsDefault = runGames(bestBot, defaultBot, cfg.games);
const t2        = ((Date.now() - start2) / 1000).toFixed(1);
process.stdout.write(`  done (${t2}s)\n`);
printResult(`Best bot vs Default (depth ${cfg.depth})`, vsDefault, cfg.games);

// ─── Summary ─────────────────────────────────────────────────────────────────

console.log('─'.repeat(60));
const overallWinRate = (vsRandom.wins + vsDefault.wins) / (cfg.games * 2);
console.log(`Overall win rate: ${(overallWinRate * 100).toFixed(1)}%  ` +
            `(${vsRandom.wins + vsDefault.wins}W / ${cfg.games * 2} games)`);
console.log('');

// ─── Helpers ─────────────────────────────────────────────────────────────────

function printResult(label, { wins, losses, draws }, total) {
  const pct = n => `${(n / total * 100).toFixed(1)}%`.padStart(6);
  const num = n => String(n).padStart(4);
  console.log('');
  console.log(`  ${label}`);
  console.log(`    Wins   ${num(wins)}   / ${total}  (${pct(wins)})`);
  console.log(`    Losses ${num(losses)} / ${total}  (${pct(losses)})`);
  console.log(`    Draws  ${num(draws)}  / ${total}  (${pct(draws)})`);
  console.log('');
}

function parseArgs(argv) {
  const opts = { ...DEFAULTS };
  for (let i = 2; i < argv.length; i++) {
    switch (argv[i]) {
      case '--games': opts.games = int(argv[++i], '--games'); break;
      case '--depth': opts.depth = int(argv[++i], '--depth'); break;
      default:
        console.error(`Unknown argument: ${argv[i]}`);
        process.exit(1);
    }
  }
  return opts;
}

function int(val, flag) {
  const n = parseInt(val, 10);
  if (isNaN(n) || n < 1) { console.error(`${flag} requires a positive integer`); process.exit(1); }
  return n;
}
