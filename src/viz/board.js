// Terminal board renderer for Connect 4.
import { EMPTY, AI, HUMAN, ROWS, COLS } from '../game/constants.js';

const R   = '\x1b[31m';  // red    — AI    (player 2 / ●)
const Y   = '\x1b[33m';  // yellow — HUMAN (player 1 / ○)
const DIM = '\x1b[2m';   // dim    — empty cell
const RST = '\x1b[0m';   // reset

function cell(token) {
  switch (token) {
    case AI:    return `${R}●${RST}`;
    case HUMAN: return `${Y}○${RST}`;
    default:    return `${DIM}·${RST}`;
  }
}

/**
 * Print a Connect 4 board to stdout with ANSI colour.
 * Row 0 is the top; pieces fall to the bottom (highest row index).
 *
 *   +---+---+---+---+---+---+---+
 *   | · | · | · | · | · | · | · |
 *   +---+---+---+---+---+---+---+
 *   | ○ | ● | ● | ○ | · | · | · |
 *   +---+---+---+---+---+---+---+
 *     1   2   3   4   5   6   7
 *
 * @param {number[][]} board   - ROWS × COLS grid (0=empty, 1=HUMAN, 2=AI)
 * @param {string}     [label] - optional label printed above the board
 */
export function printBoard(board, label = '') {
  const divider = '+' + '---+'.repeat(COLS);
  if (label) console.log(`\n  ${label}`);
  console.log(divider);
  for (let r = 0; r < ROWS; r++) {
    const row = board[r].map(t => ` ${cell(t)} `).join('|');
    console.log(`|${row}|`);
    console.log(divider);
  }
  const colNums = Array.from({ length: COLS }, (_, i) => ` ${i + 1}  `).join('');
  console.log(` ${colNums}`);
}
