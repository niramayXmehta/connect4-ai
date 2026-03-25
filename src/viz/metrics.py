# Terminal output for per-generation training stats.
# Extracted from evolution.py so both training and tools can share formatting.


def print_header(cfg, start_gen=0):
    """
    Print the training run header.

    cfg:       training configuration dict
    start_gen: last saved generation (0 = fresh run)
    """
    if start_gen > 0:
        gen_range = (f"  gens={cfg['generations']} "
                     f"(gen {start_gen + 1}–{start_gen + cfg['generations']})")
    else:
        gen_range = f"  gens={cfg['generations']}"

    print('Phase A — Evolutionary weight tuning')
    print(
        f"  pop={cfg['population_size']}  elites={cfg['elite_count']}  "
        f"depth={cfg['search_depth']}  games/matchup={cfg['games_per_matchup']}"
        f"{gen_range}  anchors={cfg['num_anchors']}"
    )
    print('')


def print_gen_line(*, gen, total, best, mean_fitness, worst_fitness,
                   draw_rate, avg_moves, elapsed, ranked):
    """
    Print a one-line generation summary plus the best-bot weights and top-3 ranking.

    gen:           absolute generation number
    total:         last generation of the run
    best:          highest-ranked bot this generation
    mean_fitness:
    worst_fitness:
    draw_rate:     fraction of games that were draws
    avg_moves:     average move count per game
    elapsed:       wall-clock ms this generation took
    ranked:        full ranked population list
    """
    secs = f'{elapsed / 1000:.1f}'
    print(
        f"Gen {gen:03d}/{total:03d} | best: {best['fitness']:.3f} | "
        f"mean: {mean_fitness:.3f} | worst: {worst_fitness:.3f} | "
        f"draws: {draw_rate * 100:.0f}% | "
        f"moves/g: {avg_moves:.1f} | {secs}s"
    )
    print(f"  weights: {fmt_weights(best['weights'])}")
    top3 = '  '.join(f"{b['id']}({b['fitness']:.3f})" for b in ranked[:3])
    print(f'  top 3: {top3}')


def fmt_weights(w):
    """
    Format a weights dict as a compact human-readable string.
    Zero-valued optional weights (depthBonus, threatPenalty) are suppressed.
    """
    parts = [
        f"centre={w.get('centreBonus', 0):.2f}",
        f"two={w.get('two', 0):.2f}",
        f"three={w.get('three', 0):.2f}",
        f"win={w.get('win', 0):.1f}",
    ]
    if w.get('depthBonus', 0) > 0:
        parts.append(f"depthBonus={w['depthBonus']:.2f}")
    if w.get('threatPenalty', 0) > 0:
        parts.append(f"threatPenalty={w['threatPenalty']:.2f}")
    return '  '.join(parts)
