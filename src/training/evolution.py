# Full evolutionary training loop — Phase A.
from ..simulation.tournament import tournament
from .mutate import mutate
from ..bots.minimax import make_minimax_bot, DEFAULT_WEIGHTS
from ..bots.random import random_bot
from ..io.persistence import load_best, save_best, save_generation, append_metrics
from ..viz.metrics import print_header, print_gen_line, fmt_weights
from ..viz.chart import save_fitness_chart
from datetime import datetime, timezone
import time

# ─── Default configuration ────────────────────────────────────────────────────

_DEFAULTS = {
    'population_size':   20,
    'elite_count':        4,
    'games_per_matchup': 20,    # raised from 10; halves tournament noise
    'search_depth':       4,    # fixed at 4 during training; use 6 for interactive play
    'generations':      100,
    'num_anchors':        3,    # fixed random-bot opponents added to each tournament
}


def _make_anchors(n):
    """Fixed random-bot anchors — provide a stable baseline signal."""
    return [{'id': f'rand_anchor_{i}', 'fn': random_bot, 'weights': None} for i in range(n)]


# ─── Public API ───────────────────────────────────────────────────────────────

def evolve(opts=None):
    """
    Run the evolutionary training loop.
    Loads the best saved weights as the seed (or uses defaults on first run).
    Resumes from the correct absolute generation number stored in best.json.
    Saves best.json, gen_NNN.json snapshots, and appends to history.json each gen.
    Saves a matplotlib fitness chart every 10 generations.

    opts: dict of partial overrides for _DEFAULTS
    Returns: best bot dict found across the entire run
    """
    if opts is None:
        opts = {}
    cfg = {**_DEFAULTS, **opts}

    # ── Seed ──────────────────────────────────────────────────────────────────
    seed      = load_best(DEFAULT_WEIGHTS)
    start_gen = seed['generation']   # 0 on first run; last saved gen on resume

    if start_gen > 0:
        print(f"Resuming from saved weights (gen {start_gen}, fitness {seed['fitness']:.3f})\n")

    best_overall = {
        'weights':    seed['weights'],
        'fitness':    seed['fitness'],
        'generation': start_gen,
        'id':         'seed',
    }

    population  = _init_population(seed['weights'], cfg['population_size'], start_gen, cfg['search_depth'])
    anchors     = _make_anchors(cfg['num_anchors'])
    total_games = 0

    # Fitness histories (current run only, for chart)
    best_history  = []
    mean_history  = []
    worst_history = []
    draw_history  = []

    print_header(cfg, start_gen)

    # ── Main loop ─────────────────────────────────────────────────────────────
    last_gen = start_gen + cfg['generations']
    gen = start_gen + 1
    while gen <= last_gen:
        gen_start = time.perf_counter()

        # 1. Tournament (anchors included for baseline signal)
        all_ranked = tournament(population + anchors, games_per_pair=cfg['games_per_matchup'])

        games_this_gen = sum(b['games_played'] for b in all_ranked) // 2
        total_games += games_this_gen

        # Strip anchor bots
        ranked = [b for b in all_ranked if not b['id'].startswith('rand_anchor_')]

        # 2. Update best overall
        best = ranked[0]
        if best['fitness'] >= best_overall['fitness']:
            best_overall = {**best, 'generation': gen}

        # 3. Generation statistics
        fitnesses   = [b['fitness'] for b in ranked]
        mean_fit    = _mean(fitnesses)
        worst_fit   = fitnesses[-1]
        total_draws = sum(b['draws'] for b in ranked)
        total_gp    = sum(b['games_played'] for b in ranked)
        draw_rate   = total_draws / total_gp if total_gp > 0 else 0
        avg_moves   = _mean([b['avg_move_count'] for b in ranked])
        elapsed_ms  = (time.perf_counter() - gen_start) * 1000

        # 4. Print generation summary
        print_gen_line(
            gen=gen, total=last_gen, best=best, mean_fitness=mean_fit,
            worst_fitness=worst_fit, draw_rate=draw_rate, avg_moves=avg_moves,
            elapsed=elapsed_ms, ranked=ranked,
        )

        # 5. Persist
        save_best(best_overall)
        save_generation(gen, best)
        append_metrics({
            'generation':       gen,
            'timestamp':        datetime.now(timezone.utc).isoformat(),
            'bestFitness':      best['fitness'],
            'meanFitness':      mean_fit,
            'worstFitness':     worst_fit,
            'drawRate':         draw_rate,
            'avgMoveCount':     avg_moves,
            'wallClockTime_ms': elapsed_ms,
            'gamesPlayed':      total_games,
            'bestWeights':      best['weights'],
        })

        # 6. Track histories for chart
        best_history.append(best['fitness'])
        mean_history.append(mean_fit)
        worst_history.append(worst_fit)
        draw_history.append(draw_rate)

        # 7. Convergence check
        elite_fitnesses = [b['fitness'] for b in ranked[:cfg['elite_count']]]
        if _has_converged(best_history, elite_fitnesses):
            if gen < last_gen:
                print(f'\nConverged at generation {gen} — stopping early.')
            save_fitness_chart(best_history, mean_history, worst_history, draw_history, start_gen)
            break

        # 8. Chart — every 10 gens
        if gen % 10 == 0:
            save_fitness_chart(best_history, mean_history, worst_history, draw_history, start_gen)

        # 9. Next generation: elites survive, rest are mutations of elites
        population = _next_generation(ranked[:cfg['elite_count']], cfg['population_size'],
                                      gen, cfg['search_depth'])
        gen += 1

    # Save chart at end of run (covers the case where last gen % 10 != 0)
    if best_history:
        save_fitness_chart(best_history, mean_history, worst_history, draw_history, start_gen)

    print(f"\nDone. Best fitness: {best_overall['fitness']:.4f} (gen {best_overall['generation']})")
    print(f"Best weights: {fmt_weights(best_overall['weights'])}")
    return best_overall


# ─── Population helpers ───────────────────────────────────────────────────────

def _make_bot(bot_id, generation, weights, depth):
    return {'id': bot_id, 'generation': generation, 'weights': weights,
            'fn': make_minimax_bot(depth, weights)}


def _init_population(seed_weights, size, generation, depth):
    pop = [_make_bot(_bot_id(generation, 0), generation, seed_weights, depth)]
    for i in range(1, size):
        pop.append(_make_bot(_bot_id(generation, i), generation, mutate(seed_weights), depth))
    return pop


def _next_generation(elites, size, generation, depth):
    # Elites carry forward unchanged (new bot object, same weights)
    next_pop = [_make_bot(e['id'], e['generation'], e['weights'], depth) for e in elites]
    i = 0
    while len(next_pop) < size:
        parent = elites[i % len(elites)]
        next_pop.append(_make_bot(_bot_id(generation, len(next_pop)), generation,
                                  mutate(parent['weights']), depth))
        i += 1
    return next_pop


# ─── Convergence ──────────────────────────────────────────────────────────────

def _has_converged(fit_history, elite_fitnesses):
    latest = fit_history[-1]
    if latest >= 0.95:
        return True

    if len(fit_history) >= 30:
        window      = fit_history[-30:]
        window_best = max(window)
        if window_best - window[0] < 0.001:
            if _variance(elite_fitnesses) < 0.005:
                return True
    return False


def _variance(arr):
    if len(arr) < 2:
        return 0
    m = sum(arr) / len(arr)
    return sum((x - m) ** 2 for x in arr) / len(arr)


# ─── Utilities ────────────────────────────────────────────────────────────────

def _mean(arr):
    return 0 if not arr else sum(arr) / len(arr)


def _bot_id(generation, index):
    return f'bot_{generation:04d}_{index:02d}'
