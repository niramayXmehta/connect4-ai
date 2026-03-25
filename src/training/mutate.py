# Mutate a weights dict by adding proportional Gaussian noise to each weight.
import random
import math

# terminalWin is structural — changing it would break the search; never mutate it.
_IMMUTABLE = {'terminalWin'}

_MUTATION_PROB = 0.5    # probability each weight changes
_SIGMA_SCALE   = 0.30   # sigma = |weight| * SIGMA_SCALE
_MIN_SIGMA     = 0.1    # floor so zero-valued weights can still evolve

# Hard caps prevent unbounded drift that drowns out weaker signals.
_CAPS = {
    'win':         200,
    'centreBonus':  10,
    'three':        20,
    'two':          10,
}


def mutate(weights):
    """
    Return a new weights dict with each mutable weight independently perturbed.

    weights: source dict (not mutated)
    Returns: new weights dict
    """
    result = {}
    for key, value in weights.items():
        if key in _IMMUTABLE:
            result[key] = value
        elif random.random() < _MUTATION_PROB:
            sigma   = max(_MIN_SIGMA, abs(value) * _SIGMA_SCALE)
            mutated = max(0, value + _gaussian(0, sigma))
            result[key] = min(mutated, _CAPS[key]) if key in _CAPS else mutated
        else:
            result[key] = value
    return result


def _gaussian(mean=0, std=1):
    """Box-Muller transform — returns a single N(mean, std) sample."""
    u = 1 - random.random()  # exclude 0 to avoid log(0)
    v = random.random()
    return mean + std * math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)
