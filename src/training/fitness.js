// Fitness formula and standalone bot evaluation against a pool.
import { runGame } from '../simulation/runner.js';

/**
 * Compute fitness from raw game stats.
 * Draws are penalised heavily — they count double in the denominator.
 * This discourages draw-farming strategies.
 *
 *   fitness = wins / (wins + losses + draws × 2)
 *
 * Returns 0 if no games have been played.
 *
 * @param {{ wins: number, losses: number, draws: number }} stats
 * @returns {number} fitness in [0, 1]
 */
export function calcFitness({ wins, losses, draws }) {
  const denominator = wins + losses + draws * 2;
  return denominator === 0 ? 0 : wins / denominator;
}

/**
 * Evaluate a single bot against every bot in `pool`.
 * Useful for one-off evaluation outside the tournament (e.g. testing Phase C bots).
 *
 * @param {{ id: string, fn: Function }} bot
 * @param {{ id: string, fn: Function }[]} pool
 * @param {number} gamesPerOpponent  - alternates first player
 * @returns {{ wins, losses, draws, fitness }}
 */
export function evaluateFitness(bot, pool, gamesPerOpponent = 10) {
  let wins = 0, losses = 0, draws = 0;

  for (const opponent of pool) {
    for (let g = 0; g < gamesPerOpponent; g++) {
      const { winner } = runGame(bot.fn, opponent.fn, { botAGoesFirst: g % 2 === 0 });
      if (winner === 'A')      wins++;
      else if (winner === 'B') losses++;
      else                     draws++;
    }
  }

  return { wins, losses, draws, fitness: calcFitness({ wins, losses, draws }) };
}
