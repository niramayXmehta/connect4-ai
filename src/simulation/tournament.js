// Round-robin tournament: every bot in the population plays every other bot.
import { runGame } from './runner.js';

/**
 * Run a full round-robin tournament over `population`.
 *
 * Each unique pair (i, j) plays `gamesPerPair` games, alternating who goes first.
 * Stats are accumulated symmetrically: a win for A is a loss for B and vice-versa.
 *
 * fitness formula (inlined from Phase A spec):
 *   fitness = wins / (wins + losses + draws × 0.5)
 *
 * @param {{ id: string, fn: Function }[]} population
 * @param {object} opts
 * @param {number} opts.gamesPerPair  default 10
 * @returns {object[]} population sorted by fitness descending, each bot augmented with:
 *   { wins, losses, draws, gamesPlayed, fitness, avgMoveCount }
 */
export function tournament(population, { gamesPerPair = 10 } = {}) {
  // Per-bot accumulators keyed by id
  const acc = new Map(
    population.map(b => [b.id, { wins: 0, losses: 0, draws: 0, totalMoves: 0, gameCount: 0 }]),
  );

  // All unique ordered pairs
  for (let i = 0; i < population.length; i++) {
    for (let j = i + 1; j < population.length; j++) {
      const a = population[i];
      const b = population[j];
      const sa = acc.get(a.id);
      const sb = acc.get(b.id);

      for (let g = 0; g < gamesPerPair; g++) {
        const { winner, moves } = runGame(a.fn, b.fn, { botAGoesFirst: g % 2 === 0 });

        if (winner === 'A')      { sa.wins++;   sb.losses++; }
        else if (winner === 'B') { sa.losses++; sb.wins++;   }
        else                     { sa.draws++;  sb.draws++;  }

        sa.totalMoves += moves;  sb.totalMoves += moves;
        sa.gameCount++;          sb.gameCount++;
      }
    }
  }

  // Attach stats and fitness to each bot, then sort best-first
  return population
    .map(bot => {
      const s = acc.get(bot.id);
      const denominator = s.wins + s.losses + s.draws * 0.5;
      const fitness = denominator === 0 ? 0 : s.wins / denominator;
      return {
        ...bot,
        wins:         s.wins,
        losses:       s.losses,
        draws:        s.draws,
        gamesPlayed:  s.gameCount,
        fitness,
        avgMoveCount: s.gameCount > 0 ? s.totalMoves / s.gameCount : 0,
      };
    })
    .sort((a, b) => b.fitness - a.fitness);
}
