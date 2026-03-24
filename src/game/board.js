// Board state management: create, place, unplace, clone
import { ROWS, COLS, EMPTY } from './constants.js';

/** Returns a fresh empty board (2D array, row 0 = top, row ROWS-1 = bottom). */
export function createBoard() {
  return Array.from({ length: ROWS }, () => new Array(COLS).fill(EMPTY));
}

/** Clone a board without sharing references. */
export function clone(board) {
  return board.map(row => row.slice());
}

/**
 * Return the lowest empty row index in col (pieces fall to the bottom).
 * Returns -1 if the column is full.
 */
export function lowestRow(board, col) {
  for (let r = ROWS - 1; r >= 0; r--) {
    if (board[r][col] === EMPTY) return r;
  }
  return -1;
}

/**
 * Place a token in the given column (mutates board).
 * Returns the row index where the token landed, or -1 if the column is full.
 */
export function place(board, col, token) {
  const row = lowestRow(board, col);
  if (row === -1) return -1;
  board[row][col] = token;
  return row;
}

/**
 * Remove the topmost token from the given column (mutates board, undoes a move).
 * Returns the row that was cleared, or -1 if the column is already empty.
 */
export function unplace(board, col) {
  for (let r = 0; r < ROWS; r++) {
    if (board[r][col] !== EMPTY) {
      board[r][col] = EMPTY;
      return r;
    }
  }
  return -1;
}
