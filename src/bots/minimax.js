// Minimax bot with alpha-beta pruning. Accepts a weights object.
import { validCols, checkWin, isFull } from '../game/rules.js';
import { place, unplace } from '../game/board.js';
import { AI, HUMAN } from '../game/constants.js';

const DEFAULT_WEIGHTS = {
  centreBonus: 3,
  three: 5,
  two: 2,
  win: 100,
  terminalWin: 1_000_000,
};

/**
 * Return the best column for `token` using minimax + alpha-beta.
 * @param {number[][]} board
 * @param {number} depth
 * @param {object} weights
 * @returns {number} column index
 */
export function minimaxBot(board, depth = 6, weights = DEFAULT_WEIGHTS) {
  // TODO: implement
}

/** Static evaluation of a board position from AI's perspective. */
function evaluate(board, weights) {
  // TODO: implement using weights
}
