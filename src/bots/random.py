# Random bot — picks a uniformly random valid column. Used as baseline.
import random as _random
from ..game.rules import valid_cols


def random_bot(board, token=None):
    """
    Pick a uniformly random valid column.
    token is accepted for interface compatibility but ignored.
    """
    cols = valid_cols(board)
    return _random.choice(cols)
