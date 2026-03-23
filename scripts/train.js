#!/usr/bin/env node
// CLI entry point: run the evolutionary training loop.
import { evolve } from '../src/training/evolution.js';

const opts = {
  // Override defaults from command-line args here if needed
};

console.log('Starting evolutionary training...');
await evolve(opts);
