// MCTS bot — Monte Carlo Tree Search with UCB1. Phase C.
import { validCols, checkWin, isFull } from '../game/rules.js';
import { clone, place } from '../game/board.js';
import { AI, HUMAN } from '../game/constants.js';

/**
 * Return the best column for `token` using MCTS.
 * @param {number[][]} board
 * @param {number} token  - AI or HUMAN
 * @param {object} opts
 * @param {number} opts.iterations  - number of simulations (default 1000)
 * @param {number} opts.C           - UCB1 exploration constant (default √2)
 * @returns {number} column index
 */
export function mctsBot(board, token, { iterations = 1000, C = Math.SQRT2 } = {}) {
  // TODO: implement selection, expansion, simulation, backpropagation
}
