// Random bot — picks a uniformly random valid column. Used as baseline.
import { validCols } from '../game/rules.js';

/**
 * @param {number[][]} board
 * @returns {number} column index
 */
export function randomBot(board) {
  const cols = validCols(board);
  return cols[Math.floor(Math.random() * cols.length)];
}
