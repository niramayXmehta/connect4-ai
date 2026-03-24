// ASCII fitness chart — printed every 10 generations during training.
//
// Example (50 gens, fitness improving from 0.55 to 0.94):
//
//   Fitness over generations
//   1.0 |
//   0.9 |                                              * * * *
//   0.8 |                        * * * * * * * * * * *
//   0.7 |            * * * * * *
//   0.6 | * * * * * *
//   0.5 |
//       +---------------------------------------------------> gen
//       7    12   17   22   27   32   37   42   47   52   56

const CHART_WIDTH = 54;   // max columns used for data points
const Y_LEVELS    = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5];

/**
 * Print an ASCII fitness chart to stdout.
 * Each data point (one per generation) is placed in the row whose label
 * equals floor(fitness × 10) / 10 — the standard 0.1-bucket rounding.
 *
 * @param {number[]} fitHistory  - bestFitness per generation, current run only
 * @param {number}   startGen    - absolute generation number before this run started (0 = fresh)
 */
export function printFitnessChart(fitHistory, startGen = 0) {
  if (fitHistory.length === 0) return;

  const n = fitHistory.length;

  // Sample down to CHART_WIDTH columns if we have more data than columns
  const cols = Array.from({ length: Math.min(n, CHART_WIDTH) }, (_, i) => {
    const idx = n <= CHART_WIDTH ? i : Math.round(i * (n - 1) / (CHART_WIDTH - 1));
    return fitHistory[idx];
  });

  console.log('');
  console.log('  Fitness over generations');

  for (const lvl of Y_LEVELS) {
    const label = lvl.toFixed(1);
    // Place a '*' at a column if that column's fitness rounds to this level.
    // Use Math.round to nearest 0.1; clamp to [0.5, 1.0] so outliers don't vanish.
    const row = cols.map(f => {
      const bucket = Math.round(Math.min(Math.max(f, 0.5), 1.0) * 10) / 10;
      return bucket === lvl ? '*' : ' ';
    }).join(' ');
    console.log(`  ${label} |${row}`);
  }

  // Axis line
  const axisLen = cols.length * 2 - 1;   // chars including spaces between data points
  console.log(`       +${'-'.repeat(axisLen)}-> gen`);

  // X-axis generation labels
  console.log(`       ${buildXAxis(startGen + 1, startGen + n, cols.length)}`);
  console.log('');
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Build the x-axis label string aligned to chart columns.
 * Labels are placed at generation numbers that are multiples of a nice interval.
 *
 * @param {number} firstGen  - absolute generation of the leftmost column
 * @param {number} lastGen   - absolute generation of the rightmost column
 * @param {number} numCols   - number of data columns (determines char positions)
 * @returns {string}
 */
function buildXAxis(firstGen, lastGen, numCols) {
  const totalWidth = numCols * 2 - 1;        // total chars including separators
  const buf = Array(totalWidth).fill(' ');

  // Pick a round interval (5, 10, 20 …) so labels don't crowd
  const range    = lastGen - firstGen || 1;
  const rawStep  = Math.ceil(range / 6);
  const interval = [1, 2, 5, 10, 20, 25, 50, 100].find(v => v >= rawStep) ?? rawStep;

  // Round firstGen up to the nearest interval multiple
  const startLabel = Math.ceil(firstGen / interval) * interval;

  for (let gen = startLabel; gen <= lastGen; gen += interval) {
    // Map generation to char position: 0-based in [0, totalWidth-1]
    const frac = (gen - firstGen) / (lastGen - firstGen || 1);
    const pos  = Math.round(frac * (totalWidth - 1));
    const str  = String(gen);
    for (let k = 0; k < str.length && pos + k < totalWidth; k++) {
      buf[pos + k] = str[k];
    }
  }

  return buf.join('');
}
