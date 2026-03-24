#!/usr/bin/env node
// CLI entry point: run the Phase A evolutionary training loop.
//
// Usage:
//   node scripts/train.js
//   node scripts/train.js --gens 50 --pop 20 --depth 4 --games 20 --elite 4
import { evolve } from '../src/training/evolution.js';

const opts = parseArgs(process.argv);

await evolve(opts);

// ─── Argument parsing ─────────────────────────────────────────────────────────

function parseArgs(argv) {
  const opts = {};
  for (let i = 2; i < argv.length; i++) {
    switch (argv[i]) {
      case '--gens':  opts.generations    = int(argv[++i], '--gens');  break;
      case '--pop':   opts.populationSize = int(argv[++i], '--pop');   break;
      case '--depth': opts.searchDepth    = int(argv[++i], '--depth'); break;
      case '--games': opts.gamesPerMatchup = int(argv[++i], '--games'); break;
      case '--elite': opts.eliteCount     = int(argv[++i], '--elite'); break;
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
