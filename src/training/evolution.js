// Full evolutionary training loop — Phase A.
import { tournament }                              from '../simulation/tournament.js';
import { mutate }                                  from './mutate.js';
import { makeMinimaxBot, DEFAULT_WEIGHTS }         from '../bots/minimax.js';
import { randomBot }                               from '../bots/random.js';
import { loadBest, saveBest, saveGeneration, appendMetrics } from '../io/persistence.js';
import { printHeader, printGenLine, fmtWeights }   from '../viz/metrics.js';
import { printFitnessChart }                       from '../viz/chart.js';

// ─── Default configuration ───────────────────────────────────────────────────

const DEFAULTS = {
  populationSize:  20,
  eliteCount:       4,
  gamesPerMatchup: 20,   // raised from 10; halves tournament noise
  searchDepth:      4,   // fixed at 4 during training; use 6 for interactive play
  generations:    100,
  numAnchors:       3,   // fixed random-bot opponents added to each tournament
};

// Fixed random-bot anchors — one instance per slot, reused every generation.
// They provide a stable baseline signal to break the structural mean=0.5 trap.
function makeAnchors(n) {
  return Array.from({ length: n }, (_, i) => ({
    id:      `rand_anchor_${i}`,
    fn:      randomBot,
    weights: null,
  }));
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Run the evolutionary training loop.
 * Loads the best saved weights as the seed (or uses defaults on first run).
 * Resumes from the correct absolute generation number stored in best.json.
 * Saves best.json, gen_NNN.json snapshots, and appends to history.json each gen.
 * Prints an ASCII fitness chart every 10 generations.
 *
 * @param {object} opts  - partial overrides for DEFAULTS
 * @returns {object}     - best bot found across the entire run
 */
export async function evolve(opts = {}) {
  const cfg = { ...DEFAULTS, ...opts };

  // ── Seed ──────────────────────────────────────────────────────────────────
  const seed     = loadBest(DEFAULT_WEIGHTS);
  const startGen = seed.generation;   // 0 on first run; last saved gen on resume

  if (startGen > 0) {
    console.log(`Resuming from saved weights (gen ${startGen}, fitness ${seed.fitness.toFixed(3)})\n`);
  }

  let bestOverall = { weights: seed.weights, fitness: seed.fitness, generation: startGen, id: 'seed' };

  let population   = initPopulation(seed.weights, cfg.populationSize, startGen, cfg.searchDepth);
  const anchors    = makeAnchors(cfg.numAnchors);
  let totalGames   = 0;
  const fitHistory = [];   // best fitness per generation (current run only, for chart + plateau check)

  printHeader(cfg, startGen);

  // ── Main loop ─────────────────────────────────────────────────────────────
  const lastGen = startGen + cfg.generations;
  for (let gen = startGen + 1; gen <= lastGen; gen++) {
    const genStart = Date.now();

    // 1. Tournament (anchors included for baseline signal, filtered out afterwards)
    const allRanked = tournament([...population, ...anchors], { gamesPerPair: cfg.gamesPerMatchup });

    // Each game is recorded in both bots' gamesPlayed → divide by 2 for actual games
    const gamesThisGen = allRanked.reduce((s, b) => s + b.gamesPlayed, 0) / 2;
    totalGames += gamesThisGen;

    // Strip anchor bots — only the minimax population matters for selection
    const ranked = allRanked.filter(b => !b.id.startsWith('rand_anchor_'));

    // 2. Update best overall
    // Use >= so a tie in fitness still updates bestOverall with the most recently
    // evolved weights, rather than preserving an early lucky result.
    const best = ranked[0];
    if (best.fitness >= bestOverall.fitness) {
      bestOverall = { ...best, generation: gen };
    }

    // 3. Generation statistics
    const fitnesses   = ranked.map(b => b.fitness);
    const meanFitness = mean(fitnesses);
    const drawRate    = ranked.reduce((s, b) => s + b.draws, 0) /
                        ranked.reduce((s, b) => s + b.gamesPlayed, 0);
    const avgMoves    = mean(ranked.map(b => b.avgMoveCount));
    const elapsed     = Date.now() - genStart;

    // 4. Print generation summary
    printGenLine({ gen, total: lastGen, best, meanFitness,
                   worstFitness: fitnesses.at(-1), drawRate, avgMoves, elapsed, ranked });

    // 5. Persist
    saveBest(bestOverall);
    saveGeneration(gen, best);
    appendMetrics({
      generation:       gen,
      timestamp:        new Date().toISOString(),
      bestFitness:      best.fitness,
      meanFitness,
      worstFitness:     fitnesses.at(-1),
      drawRate,
      avgMoveCount:     avgMoves,
      wallClockTime_ms: elapsed,
      gamesPlayed:      totalGames,
      bestWeights:      best.weights,
    });

    // 6. Convergence check
    fitHistory.push(best.fitness);
    const eliteFitnesses = ranked.slice(0, cfg.eliteCount).map(b => b.fitness);
    if (hasConverged(fitHistory, eliteFitnesses)) {
      if (gen < lastGen) {
        console.log(`\nConverged at generation ${gen} — stopping early.`);
      }
      // Print chart one final time before stopping
      printFitnessChart(fitHistory, startGen);
      break;
    }

    // 7. ASCII fitness chart — every 10 gens
    if (gen % 10 === 0) {
      printFitnessChart(fitHistory, startGen);
    }

    // 8. Next generation: elites survive, rest are mutations of elites
    population = nextGeneration(ranked.slice(0, cfg.eliteCount), cfg.populationSize, gen, cfg.searchDepth);
  }

  console.log(`\nDone. Best fitness: ${bestOverall.fitness.toFixed(4)} (gen ${bestOverall.generation})`);
  console.log(`Best weights: ${fmtWeights(bestOverall.weights)}`);
  return bestOverall;
}

// ─── Population helpers ───────────────────────────────────────────────────────

function makeBot(id, generation, weights, depth) {
  return { id, generation, weights, fn: makeMinimaxBot(depth, weights) };
}

function initPopulation(seedWeights, size, generation, depth) {
  const pop = [makeBot(botId(generation, 0), generation, seedWeights, depth)];
  for (let i = 1; i < size; i++) {
    pop.push(makeBot(botId(generation, i), generation, mutate(seedWeights), depth));
  }
  return pop;
}

function nextGeneration(elites, size, generation, depth) {
  // Elites carry forward unchanged (new bot object, same weights)
  const next = elites.map(e => makeBot(e.id, e.generation, e.weights, depth));
  let i = 0;
  while (next.length < size) {
    const parent = elites[i % elites.length];
    next.push(makeBot(botId(generation, next.length), generation, mutate(parent.weights), depth));
    i++;
  }
  return next;
}

// ─── Convergence ─────────────────────────────────────────────────────────────

function hasConverged(fitHistory, eliteFitnesses) {
  const latest = fitHistory.at(-1);
  if (latest >= 0.95) return true;                            // dominates pool

  if (fitHistory.length >= 30) {
    const window = fitHistory.slice(-30);
    const windowBest = Math.max(...window);
    // True plateau: peak fitness in the last 30 gens has not improved over
    // what was recorded 30 gens ago. Using max() instead of latest prevents
    // a single noisy bad generation from triggering early stopping.
    if (windowBest - window[0] < 0.001) {
      // Second gate: elites must also be homogeneous. If variance across
      // the top elites is still high, the population is still exploring —
      // don't stop it.
      if (variance(eliteFitnesses) < 0.005) return true;
    }
  }
  return false;
}

function variance(arr) {
  if (arr.length < 2) return 0;
  const m = arr.reduce((a, b) => a + b, 0) / arr.length;
  return arr.reduce((s, x) => s + (x - m) ** 2, 0) / arr.length;
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function mean(arr) {
  return arr.length === 0 ? 0 : arr.reduce((a, b) => a + b, 0) / arr.length;
}

function botId(generation, index) {
  return `bot_${String(generation).padStart(4, '0')}_${String(index).padStart(2, '0')}`;
}
