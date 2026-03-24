// Mutate a weights object by adding proportional Gaussian noise to each weight.

// terminalWin is structural — changing it would break the search; never mutate it.
const IMMUTABLE = new Set(['terminalWin']);

const MUTATION_PROB = 0.5;   // probability each weight changes
const SIGMA_SCALE   = 0.30;  // sigma = |weight| * SIGMA_SCALE
const MIN_SIGMA     = 0.1;   // floor so zero-valued weights can still evolve

// Hard caps prevent unbounded drift that drowns out weaker signals.
// win cap lowered to 200: population naturally converges toward 80-135,
// the 300 cap was pushing it artificially high.
const CAPS = {
  win:         200,
  centreBonus:  10,
  three:        20,
  two:          10,
};

/**
 * Return a new weights object with each mutable weight independently perturbed.
 * Probabilities, scale, and floor are per the Phase A spec.
 *
 * @param {object} weights  - source weights (not mutated)
 * @returns {object}        - new weights object
 */
export function mutate(weights) {
  const result = {};
  for (const [key, value] of Object.entries(weights)) {
    if (IMMUTABLE.has(key)) {
      result[key] = value;
    } else if (Math.random() < MUTATION_PROB) {
      const sigma = Math.max(MIN_SIGMA, Math.abs(value) * SIGMA_SCALE);
      const mutated = Math.max(0, value + gaussian(0, sigma));
      result[key] = key in CAPS ? Math.min(mutated, CAPS[key]) : mutated;
    } else {
      result[key] = value;
    }
  }
  return result;
}

/** Box-Muller transform — returns a single N(mean, std) sample. */
function gaussian(mean = 0, std = 1) {
  const u = 1 - Math.random(); // exclude 0 to avoid log(0)
  const v = Math.random();
  return mean + std * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
