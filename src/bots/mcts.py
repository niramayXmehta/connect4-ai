# MCTS bot — Monte Carlo Tree Search with UCB1. Phase C stub.
import math
from ..game.rules import valid_cols, check_win, is_full
from ..game.board import clone, place
from ..game.constants import AI, HUMAN


def mcts_bot(board, token, iterations=1000, C=math.sqrt(2)):
    """
    Return the best column for `token` using MCTS.

    board:      current board state
    token:      AI or HUMAN
    iterations: number of simulations (default 1000)
    C:          UCB1 exploration constant (default √2)
    Returns:    column index
    """
    # TODO: implement selection, expansion, simulation, backpropagation
    pass
