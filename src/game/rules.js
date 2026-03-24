// Game rules: win detection, draw detection, valid moves
import { ROWS, COLS, WIN, EMPTY } from './constants.js';

/**
 * Returns true if `token` has WIN consecutive tokens anywhere on the board.
 * Checks horizontal, vertical, and both diagonals.
 */
export function checkWin(board, token) {
  // Horizontal
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c <= COLS - WIN; c++) {
      let found = true;
      for (let i = 0; i < WIN; i++) {
        if (board[r][c + i] !== token) { found = false; break; }
      }
      if (found) return true;
    }
  }

  // Vertical
  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r <= ROWS - WIN; r++) {
      let found = true;
      for (let i = 0; i < WIN; i++) {
        if (board[r + i][c] !== token) { found = false; break; }
      }
      if (found) return true;
    }
  }

  // Diagonal down-right (\)
  for (let r = 0; r <= ROWS - WIN; r++) {
    for (let c = 0; c <= COLS - WIN; c++) {
      let found = true;
      for (let i = 0; i < WIN; i++) {
        if (board[r + i][c + i] !== token) { found = false; break; }
      }
      if (found) return true;
    }
  }

  // Diagonal up-right (/)
  for (let r = WIN - 1; r < ROWS; r++) {
    for (let c = 0; c <= COLS - WIN; c++) {
      let found = true;
      for (let i = 0; i < WIN; i++) {
        if (board[r - i][c + i] !== token) { found = false; break; }
      }
      if (found) return true;
    }
  }

  return false;
}

/** Returns true if the board is completely full (draw). */
export function isFull(board) {
  return board[0].every(cell => cell !== EMPTY);
}

/** Returns an array of column indices that are not yet full. */
export function validCols(board) {
  const cols = [];
  for (let c = 0; c < COLS; c++) {
    if (board[0][c] === EMPTY) cols.push(c);
  }
  return cols;
}
