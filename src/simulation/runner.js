// Play one or more complete games between two bots and return results.
import { createBoard, place } from '../game/board.js';
import { checkWin, isFull } from '../game/rules.js';
import { AI, HUMAN } from '../game/constants.js';

/**
 * @typedef {Object} GameResult
 * @property {'A'|'B'|null} winner  - which bot won, or null for draw
 * @property {number}       moves   - total plies played
 * @property {number}       duration - wall-clock ms
 */

/**
 * Run a single game between two bot functions.
 *
 * Token assignment: the first player always uses AI (2), second uses HUMAN (1).
 * `botAGoesFirst` controls which bot is the first player.
 *
 * @param {Function} botA  - (board, token) => colIndex
 * @param {Function} botB  - (board, token) => colIndex
 * @param {object}   opts
 * @param {boolean}  opts.botAGoesFirst  - default true
 * @returns {GameResult}
 */
export function runGame(botA, botB, { botAGoesFirst = true } = {}) {
  const board = createBoard();

  // bots[0] is the first player (token AI), bots[1] is the second (token HUMAN)
  const bots   = botAGoesFirst ? [botA, botB] : [botB, botA];
  const tokens = [AI, HUMAN];

  let moves = 0;
  const start = Date.now();

  while (true) {
    const turn  = moves % 2;
    const token = tokens[turn];
    const col   = bots[turn](board, token);

    place(board, col, token);
    moves++;

    if (checkWin(board, token)) {
      // turn 0 is first player; botA is first player iff botAGoesFirst
      const winnerIsA = (turn === 0) === botAGoesFirst;
      return { winner: winnerIsA ? 'A' : 'B', moves, duration: Date.now() - start };
    }

    if (isFull(board)) {
      return { winner: null, moves, duration: Date.now() - start };
    }
  }
}

/**
 * Run N games between botA and botB, alternating who goes first each game.
 * Returns win/loss/draw counts from botA's perspective.
 *
 * @param {Function} botA
 * @param {Function} botB
 * @param {number}   n
 * @returns {{ wins: number, losses: number, draws: number }}
 */
export function runGames(botA, botB, n = 100) {
  let wins = 0, losses = 0, draws = 0;

  for (let i = 0; i < n; i++) {
    const { winner } = runGame(botA, botB, { botAGoesFirst: i % 2 === 0 });
    if (winner === 'A')   wins++;
    else if (winner === 'B') losses++;
    else                     draws++;
  }

  return { wins, losses, draws };
}
