// Mutate a weights object by adding Gaussian noise to each weight.

/**
 * Return a new weights object with each value perturbed.
 * @param {object} weights
 * @param {number} sigma  - standard deviation of the mutation noise
 * @returns {object} mutated weights
 */
export function mutate(weights, sigma = 0.5) {
  // TODO: implement Gaussian mutation per weight key
}

/** Box-Muller transform — returns a single normally-distributed sample. */
function gaussian(mean = 0, std = 1) {
  const u = 1 - Math.random();
  const v = Math.random();
  return mean + std * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
