// All save/load operations for training state.
//
// Responsibilities:
//   loadBest       — read data/weights/best.json, merge with defaults
//   saveBest       — overwrite data/weights/best.json
//   saveGeneration — write data/weights/gen_NNN.json snapshot after each gen
//   loadHistory    — read data/metrics/history.json
//   appendMetrics  — append one entry to data/metrics/history.json
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join }  from 'node:path';

const __dirname   = dirname(fileURLToPath(import.meta.url));
const ROOT        = join(__dirname, '../..');
const WEIGHTS_DIR = join(ROOT, 'data/weights');
const BEST_PATH   = join(WEIGHTS_DIR, 'best.json');
const HIST_PATH   = join(ROOT, 'data/metrics/history.json');

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Load the best-known weights from data/weights/best.json.
 * Returns { weights, generation, fitness } with weights merged over defaultWeights
 * so that any keys added after the file was written are still present.
 * On first run (no file), returns generation=0, fitness=0, and a copy of defaultWeights.
 *
 * @param {object} defaultWeights
 * @returns {{ weights: object, generation: number, fitness: number }}
 */
export function loadBest(defaultWeights) {
  if (existsSync(BEST_PATH)) {
    try {
      const data = JSON.parse(readFileSync(BEST_PATH, 'utf8'));
      if (data.weights) {
        return {
          weights:    { ...defaultWeights, ...data.weights },
          generation: data.generation ?? 0,
          fitness:    data.fitness    ?? 0,
        };
      }
    } catch { /* corrupt file — fall through to defaults */ }
  }
  return { weights: { ...defaultWeights }, generation: 0, fitness: 0 };
}

/**
 * Overwrite data/weights/best.json with the given bot record.
 * Strips non-serialisable fields (fn) before writing.
 *
 * @param {object} bot
 */
export function saveBest(bot) {
  ensureDir(WEIGHTS_DIR);
  writeFileSync(BEST_PATH, JSON.stringify(strip(bot), null, 2));
}

/**
 * Write a per-generation snapshot to data/weights/gen_NNN.json.
 * NNN is the zero-padded absolute generation number.
 * Records the best bot of that generation (not the global bestOverall).
 *
 * @param {number} gen  - absolute generation number
 * @param {object} bot  - best bot of this generation
 */
export function saveGeneration(gen, bot) {
  ensureDir(WEIGHTS_DIR);
  const file = join(WEIGHTS_DIR, `gen_${String(gen).padStart(3, '0')}.json`);
  writeFileSync(file, JSON.stringify(strip(bot), null, 2));
}

/**
 * Read the full history array from data/metrics/history.json.
 * Returns [] if the file is missing or unreadable.
 *
 * @returns {Array}
 */
export function loadHistory() {
  if (existsSync(HIST_PATH)) {
    try { return JSON.parse(readFileSync(HIST_PATH, 'utf8')); } catch { /* empty */ }
  }
  return [];
}

/**
 * Append a single metrics entry to data/metrics/history.json.
 *
 * @param {object} entry
 */
export function appendMetrics(entry) {
  const history = loadHistory();
  history.push(entry);
  writeFileSync(HIST_PATH, JSON.stringify(history, null, 2));
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function ensureDir(dir) {
  mkdirSync(dir, { recursive: true });
}

/** Remove non-serialisable fields (fn) before writing to disk. */
function strip(bot) {
  const { fn: _fn, ...rest } = bot;
  return rest;
}
