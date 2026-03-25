# Play one or more complete games between two bots and return results.
import time
from ..game.board import create_board, place
from ..game.rules import check_win, is_full
from ..game.constants import AI, HUMAN


def run_game(bot_a, bot_b, bot_a_goes_first=True):
    """
    Run a single game between two bot functions.

    Token assignment: the first player always uses AI (2), second uses HUMAN (1).
    `bot_a_goes_first` controls which bot is the first player.

    Returns dict: { 'winner': 'A' | 'B' | None, 'moves': int, 'duration': float (ms) }
    """
    board = create_board()

    bots   = [bot_a, bot_b] if bot_a_goes_first else [bot_b, bot_a]
    tokens = [AI, HUMAN]

    moves = 0
    start = time.perf_counter()

    while True:
        turn  = moves % 2
        token = tokens[turn]
        col   = bots[turn](board, token)

        place(board, col, token)
        moves += 1

        if check_win(board, token):
            winner_is_a = (turn == 0) == bot_a_goes_first
            duration = (time.perf_counter() - start) * 1000
            return {'winner': 'A' if winner_is_a else 'B', 'moves': moves, 'duration': duration}

        if is_full(board):
            duration = (time.perf_counter() - start) * 1000
            return {'winner': None, 'moves': moves, 'duration': duration}


def run_games(bot_a, bot_b, n=100):
    """
    Run N games between bot_a and bot_b, alternating who goes first each game.
    Returns win/loss/draw counts from bot_a's perspective.

    Returns dict: { 'wins': int, 'losses': int, 'draws': int }
    """
    wins = losses = draws = 0

    for i in range(n):
        result = run_game(bot_a, bot_b, bot_a_goes_first=(i % 2 == 0))
        if result['winner'] == 'A':
            wins += 1
        elif result['winner'] == 'B':
            losses += 1
        else:
            draws += 1

    return {'wins': wins, 'losses': losses, 'draws': draws}
