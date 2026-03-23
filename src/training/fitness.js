// Fitness evaluation: score a bot by win rate against a pool of opponents.
import { runGame } from '../simulation/runner.js';

/**
 * Play `gamesPerOpponent` games against each bot in `pool` and return win rate.
 * @param {object} bot          - { weights, ... }
 * @param {object[]} pool       - array of opponent bots
 * @param {number} gamesPerOpponent
 * @returns {number} fitness in [0, 1]
 */
export async function evaluateFitness(bot, pool, gamesPerOpponent = 10) {
  // TODO: implement
}
