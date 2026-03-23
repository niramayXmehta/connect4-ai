// Board state management: create, place, unplace, clone
import { ROWS, COLS, EMPTY } from './constants.js';

/** Returns a fresh empty board (2D array, row 0 = top). */
export function createBoard() {
  return Array.from({ length: ROWS }, () => new Array(COLS).fill(EMPTY));
}

/** Clone a board without sharing references. */
export function clone(board) {
  return board.map(row => row.slice());
}

/**
 * Place a token in the given column.
 * Returns the row index where the token landed, or -1 if the column is full.
 */
export function place(board, col, token) {
  // TODO: implement
}

/**
 * Remove the top token from the given column (undo a move).
 * Returns the row that was cleared.
 */
export function unplace(board, col) {
  // TODO: implement
}

/** Return the lowest empty row index in col, or -1 if full. */
export function lowestRow(board, col) {
  // TODO: implement
}
