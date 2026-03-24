// Minimax bot with alpha-beta pruning. Accepts a weights object.
import { validCols, checkWin, isFull } from '../game/rules.js';
import { place, unplace } from '../game/board.js';
import { AI, HUMAN, ROWS, COLS, WIN, EMPTY } from '../game/constants.js';

export const DEFAULT_WEIGHTS = {
  centreBonus: 3,
  three: 5,
  two: 2,
  win: 150,   // seed raised from 100; observed convergence zone is 80-135, 150 centres exploration
  terminalWin: 1_000_000,
  depthBonus: 0,
  threatPenalty: 0,
};

/**
 * Return the best column for `token` using minimax + alpha-beta.
 * @param {number[][]} board
 * @param {number}     token    - the token this bot is playing as
 * @param {number}     depth
 * @param {object}     weights
 * @returns {number} column index
 */
export function minimaxBot(board, token, depth = 6, weights = DEFAULT_WEIGHTS) {
  const cols = orderedCols(validCols(board));
  const opponent = token === AI ? HUMAN : AI;

  let bestScore = -Infinity;
  let bestCol = cols[0];

  for (const col of cols) {
    place(board, col, token);
    const score = alphabeta(board, token, opponent, depth - 1, -Infinity, Infinity, false, weights);
    unplace(board, col);
    if (score > bestScore) {
      bestScore = score;
      bestCol = col;
    }
  }

  return bestCol;
}

/**
 * Returns a bot function bound to the given depth and weights.
 * The returned function matches the standard bot interface: (board, token) => col.
 * @param {number} depth
 * @param {object} weights
 * @returns {Function}
 */
export function makeMinimaxBot(depth = 6, weights = DEFAULT_WEIGHTS) {
  return (board, token) => minimaxBot(board, token, depth, weights);
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Alpha-beta minimax.
 * `token` is always the maximising player (the bot we're solving for).
 * `isMaximising` tracks whose turn it is at this node.
 */
function alphabeta(board, token, opponent, depth, alpha, beta, isMaximising, weights) {
  // Terminal: check if the player who just moved has won.
  // The player who just moved is the opposite of whoever moves next.
  const justMoved = isMaximising ? opponent : token;
  if (checkWin(board, justMoved)) {
    const score = justMoved === token ? weights.terminalWin : -weights.terminalWin;
    return score + (justMoved === token ? depth : -depth) * weights.depthBonus;
  }
  if (isFull(board)) return 0;
  if (depth === 0) return evaluate(board, token, weights);

  const cols = orderedCols(validCols(board));

  if (isMaximising) {
    let best = -Infinity;
    for (const col of cols) {
      place(board, col, token);
      best = Math.max(best, alphabeta(board, token, opponent, depth - 1, alpha, beta, false, weights));
      unplace(board, col);
      alpha = Math.max(alpha, best);
      if (alpha >= beta) break; // β cut-off
    }
    return best;
  } else {
    let best = Infinity;
    for (const col of cols) {
      place(board, col, opponent);
      best = Math.min(best, alphabeta(board, token, opponent, depth - 1, alpha, beta, true, weights));
      unplace(board, col);
      beta = Math.min(beta, best);
      if (alpha >= beta) break; // α cut-off
    }
    return best;
  }
}

/**
 * Heuristic evaluation of a non-terminal position from `token`'s perspective.
 * Scores all WIN-length windows and applies the centre-column bonus.
 */
function evaluate(board, token, weights) {
  const opponent = token === AI ? HUMAN : AI;
  let score = 0;

  // Centre column bonus
  const mid = Math.floor(COLS / 2);
  for (let r = 0; r < ROWS; r++) {
    if (board[r][mid] === token)    score += weights.centreBonus;
    if (board[r][mid] === opponent) score -= weights.centreBonus;
  }

  // Horizontal windows
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c <= COLS - WIN; c++) {
      score += scoreWindow(
        [board[r][c], board[r][c + 1], board[r][c + 2], board[r][c + 3]],
        token, opponent, weights,
      );
    }
  }

  // Vertical windows
  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r <= ROWS - WIN; r++) {
      score += scoreWindow(
        [board[r][c], board[r + 1][c], board[r + 2][c], board[r + 3][c]],
        token, opponent, weights,
      );
    }
  }

  // Diagonal down-right (\)
  for (let r = 0; r <= ROWS - WIN; r++) {
    for (let c = 0; c <= COLS - WIN; c++) {
      score += scoreWindow(
        [board[r][c], board[r + 1][c + 1], board[r + 2][c + 2], board[r + 3][c + 3]],
        token, opponent, weights,
      );
    }
  }

  // Diagonal up-right (/)
  for (let r = WIN - 1; r < ROWS; r++) {
    for (let c = 0; c <= COLS - WIN; c++) {
      score += scoreWindow(
        [board[r][c], board[r - 1][c + 1], board[r - 2][c + 2], board[r - 3][c + 3]],
        token, opponent, weights,
      );
    }
  }

  return score;
}

/** Score a single 4-cell window from `token`'s perspective. */
function scoreWindow(window, token, opponent, weights) {
  let tokenCount = 0;
  let oppCount = 0;
  let emptyCount = 0;

  for (const cell of window) {
    if (cell === token)    tokenCount++;
    else if (cell === opponent) oppCount++;
    else                   emptyCount++;
  }

  // Mixed window — blocked in both directions, no value
  if (tokenCount > 0 && oppCount > 0) return 0;

  // Token's threats
  if (tokenCount === 4)                        return weights.win;
  if (tokenCount === 3 && emptyCount === 1)    return weights.three;
  if (tokenCount === 2 && emptyCount === 2)    return weights.two;

  // Opponent's threats (negative)
  if (oppCount === 3 && emptyCount === 1)
    return -(weights.three * (1 + weights.threatPenalty));
  if (oppCount === 2 && emptyCount === 2)      return -weights.two;

  return 0;
}

/**
 * Sort valid columns so the centre columns are tried first —
 * dramatically improves alpha-beta pruning efficiency.
 */
function orderedCols(cols) {
  const mid = Math.floor(COLS / 2);
  return [...cols].sort((a, b) => Math.abs(a - mid) - Math.abs(b - mid));
}
