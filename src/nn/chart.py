"""
chart.py — Four-subplot training chart for the Phase B neural network.

Saved to data/metrics/nn_fitness_chart.png after every evaluation and at
the end of training.  Uses the non-interactive Agg backend (same pattern as
src/viz/chart.py) so it works headlessly on any machine.

Subplots (2 × 2):
  Top-left     Loss over iterations (line)
  Top-right    Replay-buffer size over iterations (line)
  Bottom-left  Eval win rate vs champion (scatter + dashed 0.55 threshold)
  Bottom-right Wall-clock time per iteration in seconds (line)
"""
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')          # non-interactive — no window, safe in headless
    import matplotlib.pyplot as plt
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False

_ROOT        = Path(__file__).parents[2]
_METRICS_DIR = _ROOT / 'data' / 'metrics'
_CHART_PATH  = _METRICS_DIR / 'nn_fitness_chart.png'

_PROMOTION_THRESHOLD = 0.55


def save_nn_chart(history):
    """
    Render and save the four-subplot training chart.

    Parameters
    ----------
    history : list[dict]
        Full list of per-iteration metric dicts from nn_history.json.
        Each dict must have keys: iteration, loss, buffer_size,
        wall_clock_ms, eval_win_rate (nullable).
    """
    if not _HAS_MATPLOTLIB:
        print('Warning: matplotlib not installed — skipping nn chart.')
        return
    if not history:
        return

    _METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Extract series ────────────────────────────────────────────────────────
    iters        = [h['iteration']                         for h in history]
    buffer_sizes = [h['buffer_size']                       for h in history]
    wall_secs    = [h['wall_clock_ms'] / 1000.0            for h in history]

    # Loss: skip None entries (buffer-too-small iterations)
    loss_iters   = [h['iteration'] for h in history if h['loss'] is not None]
    losses       = [h['loss']      for h in history if h['loss'] is not None]

    # Eval: only iterations where evaluation was run
    eval_iters   = [h['iteration']     for h in history if h['eval_win_rate'] is not None]
    eval_rates   = [h['eval_win_rate'] for h in history if h['eval_win_rate'] is not None]

    # ── Build figure ──────────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle('Connect4 AI — Phase B Training Metrics', fontsize=13, fontweight='bold')

    # Top-left: Loss
    ax = axes[0][0]
    if loss_iters:
        ax.plot(loss_iters, losses, '-', linewidth=1.5, color='tab:blue')
    ax.set_title('MSE Loss')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Loss')
    ax.grid(True, alpha=0.3)

    # Top-right: Buffer size
    ax = axes[0][1]
    ax.plot(iters, buffer_sizes, '-', linewidth=1.5, color='tab:green')
    ax.set_title('Replay Buffer Size')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Samples')
    ax.grid(True, alpha=0.3)

    # Bottom-left: Eval win rate
    ax = axes[1][0]
    if eval_iters:
        ax.plot(eval_iters, eval_rates,
                'o-', linewidth=1.5, markersize=5, color='tab:orange',
                label='Win rate vs champion')
    ax.axhline(_PROMOTION_THRESHOLD, linestyle='--', color='red', linewidth=1.2,
               label=f'Promotion threshold ({_PROMOTION_THRESHOLD:.0%})')
    ax.set_title('Eval Win Rate vs Champion')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Win rate')
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Bottom-right: Wall time per iteration
    ax = axes[1][1]
    ax.plot(iters, wall_secs, '-', linewidth=1.5, color='tab:purple')
    ax.set_title('Wall Time per Iteration')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Seconds')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(_CHART_PATH, dpi=100)
    plt.close(fig)
