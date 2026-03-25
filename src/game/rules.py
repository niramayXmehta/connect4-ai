# Game rules: win detection, draw detection, valid moves
from .constants import ROWS, COLS, WIN, EMPTY


def check_win(board, token):
    """
    Return True if `token` has WIN consecutive tokens anywhere on the board.
    Checks horizontal, vertical, and both diagonals.
    """
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - WIN + 1):
            if all(board[r][c + i] == token for i in range(WIN)):
                return True

    # Vertical
    for c in range(COLS):
        for r in range(ROWS - WIN + 1):
            if all(board[r + i][c] == token for i in range(WIN)):
                return True

    # Diagonal down-right (\)
    for r in range(ROWS - WIN + 1):
        for c in range(COLS - WIN + 1):
            if all(board[r + i][c + i] == token for i in range(WIN)):
                return True

    # Diagonal up-right (/)
    for r in range(WIN - 1, ROWS):
        for c in range(COLS - WIN + 1):
            if all(board[r - i][c + i] == token for i in range(WIN)):
                return True

    return False


def is_full(board):
    """Return True if the board is completely full (draw)."""
    return all(cell != EMPTY for cell in board[0])


def valid_cols(board):
    """Return a list of column indices that are not yet full."""
    return [c for c in range(COLS) if board[0][c] == EMPTY]
