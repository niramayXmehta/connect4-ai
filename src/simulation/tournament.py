# Round-robin tournament: every bot in the population plays every other bot.
import multiprocessing
from .worker import run_matchup

# Fallback depth when a bot dict has no 'depth' key (e.g. random-bot anchors).
_DEFAULT_DEPTH = 4


def tournament(population, games_per_pair=10, workers=5):
    """
    Run a full round-robin tournament over `population`.

    Each unique pair (i, j) plays `games_per_pair` games, alternating who goes first.
    Stats are accumulated symmetrically.

    fitness formula:
        fitness = wins / (wins + losses + draws * 0.5)

    population: list of dicts with keys 'id', 'weights' (None → random bot),
                and optionally 'depth'.
    workers:    number of parallel worker processes (1 = sequential).
    Returns:    population sorted by fitness descending, each bot augmented with
                wins, losses, draws, games_played, fitness, avg_move_count.
    """
    # Per-bot accumulators keyed by id
    acc = {
        b['id']: {'wins': 0, 'losses': 0, 'draws': 0, 'total_moves': 0, 'game_count': 0}
        for b in population
    }

    # Build one matchup spec per unique pair
    matchups = []
    for i in range(len(population)):
        for j in range(i + 1, len(population)):
            a = population[i]
            b = population[j]
            matchups.append({
                'bot_a_id':  a['id'],
                'bot_b_id':  b['id'],
                'weights_a': a.get('weights'),
                'weights_b': b.get('weights'),
                'depth_a':   a.get('depth', _DEFAULT_DEPTH),
                'depth_b':   b.get('depth', _DEFAULT_DEPTH),
                'games':     games_per_pair,
            })

    # Run matchups — parallel or sequential
    if workers > 1 and matchups:
        with multiprocessing.Pool(workers) as pool:
            results = pool.map(run_matchup, matchups)
    else:
        results = [run_matchup(m) for m in matchups]

    # Aggregate results into per-bot accumulators
    for r in results:
        sa = acc[r['bot_a_id']]
        sb = acc[r['bot_b_id']]

        sa['wins']   += r['wins_a'];  sb['wins']   += r['wins_b']
        sa['losses'] += r['wins_b'];  sb['losses'] += r['wins_a']
        sa['draws']  += r['draws'];   sb['draws']  += r['draws']

        total_moves = sum(r['move_counts'])
        game_count  = len(r['move_counts'])
        sa['total_moves'] += total_moves;  sb['total_moves'] += total_moves
        sa['game_count']  += game_count;   sb['game_count']  += game_count

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
