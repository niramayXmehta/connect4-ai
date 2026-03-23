// Game rules: win detection, draw detection, valid moves
import { ROWS, COLS, WIN, EMPTY } from './constants.js';

/** Returns true if `token` has won on `board`. */
export function checkWin(board, token) {
  // TODO: implement horizontal, vertical, diagonal checks
}

/** Returns true if the board is completely full (draw). */
export function isFull(board) {
  // TODO: implement
}

/** Returns an array of column indices that are not yet full. */
export function validCols(board) {
  // TODO: implement
}
