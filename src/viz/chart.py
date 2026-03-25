# Matplotlib fitness chart — saved to data/metrics/fitness_chart.png.
# Replaces the ASCII chart from the JS version.
#
# Two subplots:
#   1. Best fitness (solid), mean fitness (dashed), worst fitness (dotted) over gens
#   2. Draw rate over generations
#
# If matplotlib is not installed, falls back gracefully with a warning.
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')   # non-interactive backend — no window
    import matplotlib.pyplot as plt
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False

_ROOT        = Path(__file__).parents[2]
_METRICS_DIR = _ROOT / 'data' / 'metrics'
_CHART_PATH  = _METRICS_DIR / 'fitness_chart.png'


def save_fitness_chart(best_history, mean_history, worst_history, draw_history, start_gen=0):
    """
    Save a two-subplot fitness chart to data/metrics/fitness_chart.png.

    best_history:  best fitness per generation (current run)
    mean_history:  mean fitness per generation
    worst_history: worst fitness per generation
    draw_history:  draw rate per generation
    start_gen:     absolute generation number before this run started (0 = fresh)
    """
    if not _HAS_MATPLOTLIB:
        print('Warning: matplotlib not installed — skipping fitness chart.')
        return
    if not best_history:
        return

    _METRICS_DIR.mkdir(parents=True, exist_ok=True)

    gens = list(range(start_gen + 1, start_gen + len(best_history) + 1))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

    ax1.plot(gens, best_history,  '-',  label='Best',  linewidth=1.5)
    ax1.plot(gens, mean_history,  '--', label='Mean',  linewidth=1.5)
    ax1.plot(gens, worst_history, ':',  label='Worst', linewidth=1.5)
    ax1.set_ylabel('Fitness')
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc='lower right')
    ax1.set_title('Fitness over generations')

    ax2.plot(gens, draw_history, '-', linewidth=1.5, color='tab:orange')
    ax2.set_ylabel('Draw rate')
    ax2.set_xlabel('Generation')
    ax2.set_ylim(0, 1.05)
    ax2.set_title('Draw rate over generations')

    plt.tight_layout()
    plt.savefig(_CHART_PATH, dpi=100)
    plt.close(fig)
