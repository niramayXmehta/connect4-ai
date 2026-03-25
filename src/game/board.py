# Board state management: create, place, unplace, clone
from .constants import ROWS, COLS, EMPTY


def create_board():
    """Return a fresh empty board (2D list, row 0 = top, row ROWS-1 = bottom)."""
    return [[EMPTY] * COLS for _ in range(ROWS)]


def clone(board):
    """Clone a board without sharing references."""
    return [row[:] for row in board]


def lowest_row(board, col):
    """
    Return the lowest empty row index in col (pieces fall to the bottom).
    Returns -1 if the column is full.
    """
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1


def place(board, col, token):
    """
    Place a token in the given column (mutates board).
    Returns the row index where the token landed, or -1 if the column is full.
    """
    row = lowest_row(board, col)
    if row == -1:
        return -1
    board[row][col] = token
    return row


def unplace(board, col):
    """
    Remove the topmost token from the given column (mutates board, undoes a move).
    Returns the row that was cleared, or -1 if the column is already empty.
    """
    for r in range(ROWS):
        if board[r][col] != EMPTY:
            board[r][col] = EMPTY
            return r
    return -1
