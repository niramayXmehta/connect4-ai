// Terminal output for per-generation training stats.
// Extracted from evolution.js so both training and tools can share formatting.

/**
 * Print the training run header.
 *
 * @param {object} cfg       - training configuration
 * @param {number} startGen  - last saved generation (0 = fresh run)
 */
export function printHeader(cfg, startGen = 0) {
  const genRange = startGen > 0
    ? `  gens=${cfg.generations} (gen ${startGen + 1}–${startGen + cfg.generations})`
    : `  gens=${cfg.generations}`;
  console.log('Phase A — Evolutionary weight tuning');
  console.log(
    `  pop=${cfg.populationSize}  elites=${cfg.eliteCount}  depth=${cfg.searchDepth}` +
    `  games/matchup=${cfg.gamesPerMatchup}${genRange}  anchors=${cfg.numAnchors}`,
  );
  console.log('');
}

/**
 * Print a one-line generation summary plus the best-bot weights and top-3 ranking.
 *
 * @param {object} p
 * @param {number}   p.gen           - absolute generation number
 * @param {number}   p.total         - last generation of the run
 * @param {object}   p.best          - highest-ranked bot this generation
 * @param {number}   p.meanFitness
 * @param {number}   p.worstFitness
 * @param {number}   p.drawRate      - fraction of games that were draws
 * @param {number}   p.avgMoves      - average move count per game
 * @param {number}   p.elapsed       - wall-clock ms this generation took
 * @param {object[]} p.ranked        - full ranked population array
 */
export function printGenLine({ gen, total, best, meanFitness, worstFitness,
                               drawRate, avgMoves, elapsed, ranked }) {
  const pad  = (n, w = 3) => String(n).padStart(w, '0');
  const f    = n => n.toFixed(3);
  const secs = (elapsed / 1000).toFixed(1);

  console.log(
    `Gen ${pad(gen)}/${pad(total)} | best: ${f(best.fitness)} | mean: ${f(meanFitness)} | ` +
    `worst: ${f(worstFitness)} | draws: ${(drawRate * 100).toFixed(0)}% | ` +
    `moves/g: ${avgMoves.toFixed(1)} | ${secs}s`,
  );
  console.log(`  weights: ${fmtWeights(best.weights)}`);
  const top3 = ranked.slice(0, 3).map(b => `${b.id}(${f(b.fitness)})`).join('  ');
  console.log(`  top 3: ${top3}`);
}

/**
 * Format a weights object as a compact human-readable string.
 * Zero-valued optional weights (depthBonus, threatPenalty) are suppressed.
 *
 * @param {object} w
 * @returns {string}
 */
export function fmtWeights(w) {
  return [
    `centre=${w.centreBonus?.toFixed(2)}`,
    `two=${w.two?.toFixed(2)}`,
    `three=${w.three?.toFixed(2)}`,
    `win=${w.win?.toFixed(1)}`,
    ...(w.depthBonus    > 0 ? [`depthBonus=${w.depthBonus.toFixed(2)}`]    : []),
    ...(w.threatPenalty > 0 ? [`threatPenalty=${w.threatPenalty.toFixed(2)}`] : []),
  ].join('  ');
}
