# All save/load operations for training state.
#
# Responsibilities:
#   load_best       — read data/weights/best.json, merge with defaults
#   save_best       — overwrite data/weights/best.json
#   save_generation — write data/weights/gen_NNN.json snapshot after each gen
#   load_history    — read data/metrics/history.json
#   append_metrics  — append one entry to data/metrics/history.json
import json
from pathlib import Path

_ROOT        = Path(__file__).parents[2]
_WEIGHTS_DIR = _ROOT / 'data' / 'weights'
_BEST_PATH   = _WEIGHTS_DIR / 'best.json'
_HIST_PATH   = _ROOT / 'data' / 'metrics' / 'history.json'

# ─── Public API ───────────────────────────────────────────────────────────────


def load_best(default_weights):
    """
    Load the best-known weights from data/weights/best.json.
    Returns dict { weights, generation, fitness } with weights merged over default_weights
    so that any keys added after the file was written are still present.
    On first run (no file), returns generation=0, fitness=0, and a copy of default_weights.
    """
    if _BEST_PATH.exists():
        try:
            data = json.loads(_BEST_PATH.read_text(encoding='utf-8'))
            if data.get('weights'):
                return {
                    'weights':    {**default_weights, **data['weights']},
                    'generation': data.get('generation', 0),
                    'fitness':    data.get('fitness', 0),
                }
        except Exception:
            pass  # corrupt file — fall through to defaults
    return {'weights': dict(default_weights), 'generation': 0, 'fitness': 0}


def save_best(bot):
    """
    Overwrite data/weights/best.json with the given bot record.
    Strips non-serialisable fields (fn) before writing.
    """
    _WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    _BEST_PATH.write_text(json.dumps(_strip(bot), indent=2), encoding='utf-8')


def save_generation(gen, bot):
    """
    Write a per-generation snapshot to data/weights/gen_NNN.json.
    NNN is the zero-padded absolute generation number.
    Records the best bot of that generation (not the global best_overall).
    """
    _WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    path = _WEIGHTS_DIR / f'gen_{gen:03d}.json'
    path.write_text(json.dumps(_strip(bot), indent=2), encoding='utf-8')


def load_history():
    """
    Read the full history array from data/metrics/history.json.
    Returns [] if the file is missing or unreadable.
    """
    if _HIST_PATH.exists():
        try:
            return json.loads(_HIST_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
    return []


def append_metrics(entry):
    """Append a single metrics entry to data/metrics/history.json."""
    _HIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.append(entry)
    _HIST_PATH.write_text(json.dumps(history, indent=2), encoding='utf-8')


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _strip(bot):
    """Remove non-serialisable fields (fn) before writing to disk."""
    return {k: v for k, v in bot.items() if k != 'fn'}
