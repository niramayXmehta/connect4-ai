# Fitness formula and standalone bot evaluation against a pool.
from ..simulation.runner import run_game


def calc_fitness(wins, losses, draws):
    """
    Compute fitness from raw game stats.
    Draws are penalised heavily — they count double in the denominator.
    This discourages draw-farming strategies.

        fitness = wins / (wins + losses + draws * 2)

    Returns 0 if no games have been played.
    """
    denominator = wins + losses + draws * 2
    return 0 if denominator == 0 else wins / denominator


def evaluate_fitness(bot, pool, games_per_opponent=10):
    """
    Evaluate a single bot against every bot in `pool`.
    Useful for one-off evaluation outside the tournament.

    bot:  dict with 'id' and 'fn'
    pool: list of dicts with 'id' and 'fn'
    Returns: dict { wins, losses, draws, fitness }
    """
    wins = losses = draws = 0

    for opponent in pool:
        for g in range(games_per_opponent):
            result = run_game(bot['fn'], opponent['fn'], bot_a_goes_first=(g % 2 == 0))
            if result['winner'] == 'A':
                wins += 1
            elif result['winner'] == 'B':
                losses += 1
            else:
                draws += 1

    return {'wins': wins, 'losses': losses, 'draws': draws,
            'fitness': calc_fitness(wins, losses, draws)}
