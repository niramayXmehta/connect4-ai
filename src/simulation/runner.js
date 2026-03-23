// Play one complete game between two bots and return the result.
import { createBoard } from '../game/board.js';
import { checkWin, isFull, validCols } from '../game/rules.js';
import { AI, HUMAN } from '../game/constants.js';

/**
 * @typedef {Object} GameResult
 * @property {number|null} winner  - AI, HUMAN, or null for draw
 * @property {number} moves        - total plies played
 */

/**
 * Run a single game between two bot functions.
 * @param {Function} botA  - (board, token) => colIndex
 * @param {Function} botB  - (board, token) => colIndex
 * @param {object}   opts
 * @param {boolean}  opts.botAGoesFirst  - default true
 * @returns {GameResult}
 */
export function runGame(botA, botB, { botAGoesFirst = true } = {}) {
  // TODO: implement game loop
}

/**
 * Run N games between botA and botB, alternating who goes first.
 * @param {Function} botA
 * @param {Function} botB
 * @param {number}   n
 * @returns {{ wins: number, losses: number, draws: number }}
 */
export function runGames(botA, botB, n = 100) {
  // TODO: implement
}
