# Round-robin tournament: every bot in the population plays every other bot.
from .runner import run_game


def tournament(population, games_per_pair=10):
    """
    Run a full round-robin tournament over `population`.

    Each unique pair (i, j) plays `games_per_pair` games, alternating who goes first.
    Stats are accumulated symmetrically.

    fitness formula:
        fitness = wins / (wins + losses + draws * 0.5)

    population: list of dicts with keys 'id' and 'fn'
    Returns: population sorted by fitness descending, each bot augmented with
        wins, losses, draws, games_played, fitness, avg_move_count
    """
    # Per-bot accumulators keyed by id
    acc = {
        b['id']: {'wins': 0, 'losses': 0, 'draws': 0, 'total_moves': 0, 'game_count': 0}
        for b in population
    }

    # All unique ordered pairs
    for i in range(len(population)):
        for j in range(i + 1, len(population)):
            a = population[i]
            b = population[j]
            sa = acc[a['id']]
            sb = acc[b['id']]

            for g in range(games_per_pair):
                result = run_game(a['fn'], b['fn'], bot_a_goes_first=(g % 2 == 0))
                winner = result['winner']
                moves  = result['moves']

                if winner == 'A':
                    sa['wins']   += 1
                    sb['losses'] += 1
                elif winner == 'B':
                    sa['losses'] += 1
                    sb['wins']   += 1
                else:
                    sa['draws'] += 1
                    sb['draws'] += 1

                sa['total_moves'] += moves
                sb['total_moves'] += moves
                sa['game_count']  += 1
                sb['game_count']  += 1

    # Attach stats and fitness to each bot, then sort best-first
    ranked = []
    for bot in population:
        s = acc[bot['id']]
        denominator = s['wins'] + s['losses'] + s['draws'] * 0.5
        fitness = 0 if denominator == 0 else s['wins'] / denominator
        ranked.append({
            **bot,
            'wins':           s['wins'],
            'losses':         s['losses'],
            'draws':          s['draws'],
            'games_played':   s['game_count'],
            'fitness':        fitness,
            'avg_move_count': s['total_moves'] / s['game_count'] if s['game_count'] > 0 else 0,
        })

    ranked.sort(key=lambda b: b['fitness'], reverse=True)
    return ranked
