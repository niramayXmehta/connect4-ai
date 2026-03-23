// Full evolutionary training loop (Phase A).
import { evaluateFitness } from './fitness.js';
import { mutate } from './mutate.js';
// TODO (A3): import persistence helpers once src/io/persistence.js is implemented
// import { loadBest, saveBest, saveGeneration } from '../io/persistence.js';
// TODO (A4): import metrics helpers once src/io/metrics.js is implemented
// import { appendMetrics } from '../io/metrics.js';

const DEFAULTS = {
  populationSize: 20,
  generations: 100,
  eliteCount: 4,
  sigma: 0.5,
  gamesPerOpponent: 10,
};

/**
 * Run the evolutionary loop.
 * @param {object} opts - overrides for DEFAULTS
 */
export async function evolve(opts = {}) {
  const config = { ...DEFAULTS, ...opts };
  // TODO: implement initialise → evaluate → select → mutate → repeat
}
