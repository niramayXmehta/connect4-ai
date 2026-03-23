// Round-robin tournament between a pool of bots.
import { runGames } from './runner.js';

/**
 * Run a full round-robin tournament.
 * Every bot plays every other bot `gamesPerPair` games.
 * @param {object[]} bots          - array of bot descriptors with a .fn property
 * @param {number}   gamesPerPair
 * @returns {object[]} bots sorted by win rate descending, with stats attached
 */
export async function tournament(bots, gamesPerPair = 10) {
  // TODO: implement round-robin matchup schedule and aggregate results
}
