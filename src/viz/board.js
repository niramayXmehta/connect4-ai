// Print a Connect 4 board to the terminal.
import { ROWS, COLS, HUMAN, AI, EMPTY } from '../game/constants.js';

const SYMBOLS = {
  [EMPTY]: '.',
  [HUMAN]: 'X',
  [AI]: 'O',
};

/** Render the board to stdout. */
export function printBoard(board) {
  // TODO: implement coloured terminal output
  for (const row of board) {
    console.log(row.map(cell => SYMBOLS[cell]).join(' '));
  }
  console.log(Array.from({ length: COLS }, (_, i) => i).join(' '));
}
