# Terminal board renderer for Connect 4.
from ..game.constants import EMPTY, AI, HUMAN, ROWS, COLS

R   = '\x1b[31m'   # red    — AI    (player 2 / ●)
Y   = '\x1b[33m'   # yellow — HUMAN (player 1 / ○)
DIM = '\x1b[2m'    # dim    — empty cell
RST = '\x1b[0m'    # reset


def _cell(token):
    if token == AI:
        return f'{R}●{RST}'
    if token == HUMAN:
        return f'{Y}○{RST}'
    return f'{DIM}·{RST}'


def print_board(board, label=''):
    """
    Print a Connect 4 board to stdout with ANSI colour.
    Row 0 is the top; pieces fall to the bottom (highest row index).

      +---+---+---+---+---+---+---+
      | · | · | · | · | · | · | · |
      +---+---+---+---+---+---+---+
      | ○ | ● | ● | ○ | · | · | · |
      +---+---+---+---+---+---+---+
        1   2   3   4   5   6   7

    board: ROWS × COLS grid (0=empty, 1=HUMAN, 2=AI)
    label: optional label printed above the board
    """
    divider = '+' + '---+' * COLS
    if label:
        print(f'\n  {label}')
    print(divider)
    for r in range(ROWS):
        row = '|'.join(f' {_cell(board[r][c])} ' for c in range(COLS))
        print(f'|{row}|')
        print(divider)
    col_nums = ''.join(f' {i + 1}  ' for i in range(COLS))
    print(f' {col_nums}')
