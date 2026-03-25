# Worker function for parallel tournament matchups.
#
# run_matchup must be a top-level function — multiprocessing.Pool pickles it
# by (module, qualname), so lambdas and local functions are not allowed.
#
# Bots are NOT passed across process boundaries (functions aren't reliably
# picklable). Instead, weight dicts and depth are sent; each worker
# reconstructs the bot from scratch.
from .runner import run_game
from ..bots.minimax import make_minimax_bot
from ..bots.random import random_bot


def _bot_from_spec(weights, depth):
    """Reconstruct a callable bot from its serialisable spec."""
    if weights is None:
        return random_bot
    return make_minimax_bot(depth, weights)


def run_matchup(args):
    """
    Play all games for one unique pair and return aggregated results.

    args keys:
        bot_a_id   (str)
        bot_b_id   (str)
        weights_a  (dict | None)  — None → random bot
        weights_b  (dict | None)
        depth_a    (int)
        depth_b    (int)
        games      (int)          — number of games to play

    Returns dict:
        bot_a_id, bot_b_id, wins_a, wins_b, draws, move_counts (list[int])
    """
    bot_a = _bot_from_spec(args['weights_a'], args['depth_a'])
    bot_b = _bot_from_spec(args['weights_b'], args['depth_b'])

    wins_a = wins_b = draws = 0
    move_counts = []

    for g in range(args['games']):
        result = run_game(bot_a, bot_b, bot_a_goes_first=(g % 2 == 0))
        winner = result['winner']
        if winner == 'A':
            wins_a += 1
        elif winner == 'B':
            wins_b += 1
        else:
            draws += 1
        move_counts.append(result['moves'])

    return {
        'bot_a_id':    args['bot_a_id'],
        'bot_b_id':    args['bot_b_id'],
        'wins_a':      wins_a,
        'wins_b':      wins_b,
        'draws':       draws,
        'move_counts': move_counts,
    }
