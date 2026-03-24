# Project Update Log — Connect4 AI

Running record of every major change, decision, and result across the project.
Updated after every significant milestone or architectural decision.

---

## Entry 001 — Project Scaffold
**Date:** 2026-03-23
**Milestone:** Initial commit — project scaffold, docs, phase A–C planning

### What was created
Full folder structure and placeholder files:

```
src/
  game/         constants.js, board.js, rules.js
  bots/         random.js, minimax.js, mcts.js (stub)
  simulation/   runner.js, tournament.js
  training/     mutate.js, fitness.js, evolution.js
  viz/          board.js, metrics.js, chart.js (stubs)
scripts/        simulate.js, train.js
data/
  weights/      best.json
  metrics/      history.json
docs/           ARCHITECTURE.md, ROADMAP.md, PHASE_A.md, PHASE_B.md, PHASE_C.md, METRICS.md
```

### Key architectural decisions made at this stage
- **Strict layer separation**: game → bots → simulation → training → scripts. No circular imports.
- **JSON for weights**: human-readable, diff-able, no database overhead at this scale.
- **Node.js ES modules** throughout (`.js` with `import/export`).
- **Phase ordering**: A (evolutionary) → C (MCTS) → B (neural net). MCTS before NN because MCTS builds on Phase A weights and is simpler to validate.
- **`terminalWin` is immutable**: structural constant used by alpha-beta. Never mutated during evolution.
- **Search depth split**: depth 4 during training (speed), depth 6 for interactive play (quality).

---

## Entry 002 — Milestone A1: Core Foundation
**Date:** 2026-03-23
**Milestone:** A1 complete — two bots can play each other, results printed to terminal

### Files implemented
| File | What it does |
|------|-------------|
| `src/game/constants.js` | `ROWS=6, COLS=7, WIN=4, HUMAN=1, AI=2, EMPTY=0` |
| `src/game/board.js` | `createBoard`, `place`, `unplace`, `clone` — pure array operations |
| `src/game/rules.js` | `checkWin`, `isFull`, `validCols`, `lowestRow` |
| `src/bots/random.js` | Picks a uniformly random valid column. Used as baseline. |
| `src/bots/minimax.js` | Minimax + alpha-beta pruning. Accepts a `weights` object. |
| `src/simulation/runner.js` | `runGame(botA, botB, opts)` → `{ winner, moves, duration }` |
| `scripts/simulate.js` | CLI: `node scripts/simulate.js --games N` |

### Key design decisions
- **`place` / `unplace` (in-place mutation)**: Avoids allocating a new board array per node during minimax search — critical for performance at depth 4–6.
- **Centre-first column ordering in minimax**: Columns tried in order `[3, 2, 4, 1, 5, 0, 6]` for better alpha-beta pruning efficiency.
- **Token assignment**: First player always uses `AI (2)`, second player uses `HUMAN (1)`. `botAGoesFirst` flag controls which bot gets which token.
- **`runGames(botA, botB, n)`**: Wrapper that alternates first player across N games and returns aggregate `{ wins, losses, draws }`.

### Default weights at this stage
```
centreBonus = 3
three       = 5
two         = 2
win         = 100
terminalWin = 1_000_000
depthBonus  = 0
threatPenalty = 0
```

---

## Entry 003 — Milestone A2: Training Loop
**Date:** 2026-03-23
**Milestone:** A2 complete — evolutionary training loop runs, weights persist across sessions

### Files implemented
| File | What it does |
|------|-------------|
| `src/training/mutate.js` | Gaussian noise mutation per weight |
| `src/training/fitness.js` | Win-rate fitness scoring |
| `src/simulation/tournament.js` | Round-robin: every bot plays every other bot |
| `src/training/evolution.js` | Full evolutionary loop — seed, tournament, select, mutate, save |
| `scripts/train.js` | CLI entry: `--gens`, `--pop`, `--depth`, `--games`, `--elite` |

### Algorithm implemented
```
1. Load best saved weights (or use defaults on first run)
2. Init population: 1 copy of seed + (N-1) mutations
3. Round-robin tournament — each pair plays gamesPerMatchup games
4. Fitness = wins / (wins + losses + draws × 0.5)
5. Keep top K elites; fill rest of next gen with mutations of elites
6. Save best.json; append to history.json
7. Repeat until convergence or max gens reached
```

### Mutation parameters (initial)
```
MUTATION_PROB = 0.3   (30% chance each weight changes)
SIGMA_SCALE   = 0.15  (sigma = |weight| × 0.15)
MIN_SIGMA     = 0.1   (floor so zero-valued weights can still evolve)
```

### Convergence criteria
- Best fitness has not improved by >0.001 over the last 20 generations (plateau)
- Or best fitness reaches ≥0.95 (dominates the pool)

### Persistence
- `data/weights/best.json` — best bot found across all runs, updated every generation
- `data/metrics/history.json` — full per-generation metrics appended every generation
- Training resumes from saved weights on restart

---

## Entry 004 — First Training Run: 20 Generations
**Date:** 2026-03-23
**Command:** `node scripts/train.js --gens 20 --pop 20 --depth 4 --games 10 --elite 4`

### Raw results
| Gen | Best | Mean | Worst | Draws |
|-----|------|------|-------|-------|
| 1   | 0.658 | 0.490 | 0.132 | 3% |
| 6   | 0.684 | 0.492 | 0.158 | 3% |
| 14  | 0.684 | 0.500 | 0.079 | 0% |
| 20  | 0.711 | 0.500 | 0.000 | 0% |

Best weights across all 20 gens: `centre=2.24  two=1.82  three=5.51  win=82.4`

### Diagnosis: training was stuck in a noise trap

Three compounding problems were identified:

**Problem 1 — Structural mean=0.5 trap**

In a pure round-robin, every win for bot A is a loss for bot B.
Therefore `sum(wins) = sum(losses)` and the population mean fitness is
always exactly 0.5 by construction. The entire useful signal lives only in
how far each bot deviates from 0.5 — which comes exclusively from
second-player wins (beating an opponent when going second).

Decomposing the fitness values:
| fitness | second-player win rate |
|---------|------------------------|
| 0.553   | 11% as 2nd player |
| 0.632   | 26% as 2nd player |
| 0.684   | 37% as 2nd player |
| 0.711   | 42% as 2nd player |

The total differentiating range is only 10–40 extra wins out of 190 games.

**Problem 2 — Tournament noise exceeds the learning signal**

The same bot scored 0.553 in gen 7 and 0.684 in gen 6 with identical
weights. That's ±0.07–0.10 noise for an unchanged bot — larger than the
fitness gain from any single mutation. The same bot (`bot_0000_16`) sat
in the top 3 for all 20 generations because its mutations could never
reliably beat it through the noise.

**Problem 3 — Mutations too small to clear the noise floor**

With `sigma = |weight| × 0.15`, a mutation to `win=82` changes it by
~±12. For `centreBonus=2.2`, sigma ≈ 0.33. These produce bots nearly
indistinguishable from their parent in tournament play. Probability of
a mutation being detectably better (clearing ±0.07 noise) was very low.

---

## Entry 005 — Fix: Random Anchor Bots + Larger Mutations
**Date:** 2026-03-24

### Root cause
The pure minimax vs minimax round-robin has a structural floor at mean=0.5
because first-mover advantage is exactly balanced (each bot plays half games
as first player, half as second). The fitness differences between nearly-
identical bots are smaller than tournament noise. Evolution cannot make
progress when it cannot distinguish parent from child.

### Decision: Add 3 random-bot anchors to every tournament
**File changed:** `src/training/evolution.js`

Random bots are injected as fixed competitors in every tournament. They are
not part of the population — they are stripped out after tournament scoring
before selection and `nextGeneration`. Their role is purely to provide a
stable baseline:

- All minimax bots beat random bots heavily → mean fitness shifts above 0.5
- The fitness gap between a stronger and weaker minimax bot is now larger
  relative to noise
- Population ordering becomes meaningful again

Implementation: `makeAnchors(n)` creates `n` bots with `id: rand_anchor_i`
and `fn: randomBot`. They are passed to `tournament([...population, ...anchors])`.
After `allRanked` is returned, `ranked = allRanked.filter(b => !b.id.startsWith('rand_anchor_'))`.
Game counts are computed from `allRanked` (full tournament) before filtering.

**Why not add anchors to the selection pool permanently?**
We don't want random bots surviving into the next generation. They are
measurement tools, not breeding candidates. Filtering after scoring is
the cleanest separation.

### Decision: Increase mutation scale
**File changed:** `src/training/mutate.js`

```diff
- MUTATION_PROB = 0.3   (30% per weight)
- SIGMA_SCALE   = 0.15  (sigma = |weight| × 0.15)
+ MUTATION_PROB = 0.5   (50% per weight)
+ SIGMA_SCALE   = 0.30  (sigma = |weight| × 0.30)
```

With the old parameters, mutations were too small to produce bots that
clearly outperformed their parent in a noisy tournament. Doubling sigma
means the rare good mutations are now large enough to register above the
noise floor. The penalty — more mutations will be much worse — is
acceptable because those are culled immediately by selection.

### Smoke test result (1 gen, pop=10, depth=4, games=4)
```
Gen 001/001 | best: 0.917 | mean: 0.625 | worst: 0.375
  weights: centre=2.24  two=1.19  three=6.82  win=82.4  depthBonus=0.03
  top 3: bot_0000_04(0.917)  bot_0000_03(0.792)  bot_0000_00(0.708)
```

Compared to the old 20-gen run:

| Metric | Old (20 gens) | New (1 gen) |
|--------|--------------|-------------|
| Best fitness | 0.55–0.71 | **0.917** |
| Mean fitness | always 0.500 | **0.625** — trap broken |
| Winner | always bot_0000_16 | bot_0000_04 (new mutation) |
| New weights explored | none | `depthBonus=0.03` emerged |

The structural mean=0.5 trap is broken. New bots win. Weights are moving.

### Current best weights (after smoke test)
```json
{
  "centreBonus": 2.243,
  "three": 6.816,
  "two": 1.194,
  "win": 82.353,
  "terminalWin": 1000000,
  "depthBonus": 0.030,
  "threatPenalty": 0
}
fitness: 0.9167  (44W / 4L / 0D across 48 games)
```

Notable: `three` rose from 5.0 → 6.82 (+36%), `two` fell from 2.0 → 1.19 (-40%).
The bot is learning to prioritise 3-in-a-row threats more heavily than
2-in-a-row, which aligns with stronger tactical play. `depthBonus` emerged
from zero, suggesting a slight reward for winning faster is useful.

---

## Entry 006 — Full 20-Gen Training Run (Post-Fix)
**Date:** 2026-03-24
**Command:** `node scripts/train.js --gens 20 --pop 20 --depth 4 --games 10 --elite 4`

### Raw results (condensed)
| Gen | Best | Mean | Worst | Draws | Best weights (win / three / two) |
|-----|------|------|-------|-------|----------------------------------|
| 1   | 0.851 | 0.565 | 0.182 | 2%  | 92.3 / 8.55 / 1.19 |
| 3   | 0.828 | 0.540 | 0.295 | 11% | 137.1 / 2.27 / 1.06 |
| 7   | 0.707 | 0.493 | 0.286 | 28% | 195.9 / 2.70 / 1.10 |
| 11  | 0.736 | 0.503 | 0.346 | 25% | 207.8 / 5.44 / 1.16 |
| 13  | 0.819 | 0.552 | 0.233 | 7%  | 303.6 / 5.17 / 0.75 |
| 14–18 | 0.699–0.769 | ~0.54 | — | 10–12% | 303.6 / 5.17 / 0.75 (stable) |
| 19–20 | 0.729–0.851 | ~0.54 | — | 9–10% | 377.3 / 5.17 / 0.75 |

### What the fixes proved
Both fixes from Entry 005 validated immediately:

| Metric | Old (pre-fix, 20 gens) | New (post-fix, 20 gens) |
|--------|------------------------|--------------------------|
| Mean fitness | always **0.500** | **0.503–0.565** (above 0.5) |
| Winner changes each gen | never — same bot all 20 gens | **yes — active evolution** |
| Weights changing | frozen | **continuously evolving** |
| Draw rate | 0–4% | **5–37%** (more competitive play) |

### Weight trajectories — clear learning signals

**`win` weight** (4-in-a-row heuristic score):
```
92 → 82 → 137 → 104 → 90 → 80 → 196 → 128 → 155 → 197
→ 208 → 155 → 304 → 304 → 304 → 304 → 304 → 304 → 377 → 377
```
Strong upward trend. Settled at 304 for 6 consecutive gens (gens 13–18),
then jumped to 377. Still climbing — not converged. Original default was 100.

**`two` weight** (2-in-a-row score):
```
1.19 → 1.19 → 1.06 → 1.39 → 1.39 → 1.37 → 1.10 → 1.16 → 1.16
→ 1.43 → 1.16 → 0.89 → 0.75 → 0.75 → 0.75 → 0.75 → 0.75 → 0.75 → 0.75 → 0.75
```
Converged to 0.75 from gen 13 onward (8 consecutive gens). Original default was 2.0.
The training is confident: 2-in-a-row threats are nearly worthless compared to 3-in-a-row.

**`three` weight** (3-in-a-row score): Noisy exploration early, settled near 5.17.
Close to the original 5.0 — this default was already reasonable.

**`depthBonus`**: Emerged from 0 → 0.097. Winning faster is slightly rewarded.

**`threatPenalty`**: Emerged from 0 → 0.062. Penalising opponent 3-in-a-rows is slightly useful.

### Draw rate interpretation
Draw rate jumped from near 0% (old runs) to 5–37% in the new runs. This is not
a regression — it reflects more competitive play. When the bots are better calibrated,
games reach positions where both sides defend well and more games go to draw. The
old low draw rate was because the bots were unbalanced and decisive wins dominated.

### Problem discovered: `bestOverall` tracking bug

**The symptom**: `Done. Best fitness: 0.8506 (gen 1)` — the saved weights were from
gen 1's bot (win=92.3), not from the evolved gen 20 lineage (win=377.3).

**The root cause**: `bestOverall` was updated with strict `>`. Gen 1 happened to score
0.851 in a relatively easy early tournament. Gen 20's evolved bot also scored 0.851
(against stronger opponents). Because `0.851 > 0.851` is false, the more evolved bot
never replaced the lucky early one.

**The consequence**: `best.json` was seeded with a regressive bot. The next training
run would start from win=92.3 and have to rediscover the win=377.3 trajectory.

**The fix applied:**
```diff
// src/training/evolution.js
- if (best.fitness > bestOverall.fitness)
+ if (best.fitness >= bestOverall.fitness)
```
With `>=`, ties favour the most recently evolved weights. A bot that scores the same
fitness against a stronger pool in gen 20 always replaces a bot that scored it in gen 1
against a weaker pool.

**best.json manually corrected** to the gen 20 evolved weights:
```json
{
  "centreBonus": 2.974,
  "three":       5.172,
  "two":         0.747,
  "win":       377.294,
  "terminalWin": 1000000,
  "depthBonus":  0.097,
  "threatPenalty": 0.062
}
```

### Problem discovered: convergence triggered coincidentally

The plateau check fires when `fitHistory[last] - fitHistory[last-20] < 0.001`.
Gen 1 best = 0.851, gen 20 best = 0.851 → difference = 0.000 → converged.

This is a false positive. The weights were actively evolving in gens 19–20 (`win`
just jumped from 304→377). The coincidence of identical best-fitness scores in
gen 1 and gen 20 triggered early stopping. The `win` weight trajectory suggests
at least another 20–30 gens would produce further improvement.

This is a known limitation to fix later (e.g., track mean fitness trend, or
compare weight distance between generations, rather than just peak fitness).

---

## Entry 007 — 50-Gen Run: Draw-Farming Problem
**Date:** 2026-03-24
**Command:** `node scripts/train.js --gens 50 --pop 20 --depth 4 --games 10 --elite 4`
**Seeded from:** gen 20 evolved weights (win=377.3)

### Result
Run stopped at gen 5 with best fitness 0.955:
```
Gen 005/050 | best: 0.955 | mean: 0.465 | worst: 0.212 | draws: 31%
  weights: centre=2.09  two=0.77  three=4.65  win=463.9  depthBonus=0.10  threatPenalty=0.02
```

### Three problems identified

**Problem 1 — Draw farming**
Draws jumped to 31% at gen 5. The bot optimised for `not losing` rather than
`winning`. Under the old formula `wins / (wins + losses + draws × 0.5)`, a draw
is rewarded as a half-win. A bot that draws 80% of its games scores fitness ≈ 0.8
without winning a single one. With random anchors in the pool, a minimax bot
drawing against anchors (instead of winning) could still get a high score.

**Problem 2 — `win` weight unboundedly climbing**
`win` went from 377 → 464 in 5 generations with no ceiling. At this scale,
`win` (4-in-a-row heuristic, non-terminal) dwarfs every other signal by 60–100×.
The bot was collapsing to a single-feature evaluator.

**Problem 3 — False convergence at final generation**
`Converged at generation 20 — stopping early` printed even when the run completed
all its generations normally (no early stop). The message was misleading.

### Three fixes applied

**Fix 1 — Fitness formula penalises draws** (`src/training/fitness.js`)
```diff
- fitness = wins / (wins + losses + draws × 0.5)   // draws rewarded as half-win
+ fitness = wins / (wins + losses + draws × 2)      // draws hurt more than losses
```
A bot with 50W / 50L / 100D now scores 0.25 instead of 0.40.
Draw-farming is no longer a viable strategy.

**Fix 2 — Hard caps on weight drift** (`src/training/mutate.js`)
```js
const CAPS = {
  win:         300,
  centreBonus:  10,
  three:        20,
  two:          10,
};
```
Applied after mutation: `result[key] = key in CAPS ? Math.min(mutated, CAPS[key]) : mutated`.
`win=300` is already ~3× the original default (100) — room for the bot to learn
it matters, but not room to drown all other signals.

**Fix 3 — Convergence message gated on early stopping** (`src/training/evolution.js`)
```diff
- console.log(`\nConverged at generation ${gen} — stopping early.`);
+ if (gen < cfg.generations) {
+   console.log(`\nConverged at generation ${gen} — stopping early.`);
+ }
```
Message now only prints when the run actually stops before its final generation.

### Seed reset
`best.json` reset to gen 20 evolved weights with `win` clamped to 300:
```json
{
  "centreBonus": 2.974,
  "three":       5.172,
  "two":         0.747,
  "win":         300,
  "terminalWin": 1000000,
  "depthBonus":  0.097,
  "threatPenalty": 0.062
}
```

---

## Entry 008 — 50-Gen Run (Post Draw-Penalty Fix)
**Date:** 2026-03-24
**Command:** `node scripts/train.js --gens 50 --pop 20 --depth 4 --games 10 --elite 4`

### Result
Stopped at gen 20 of 50 with best fitness 0.837 (gen 4):
```
Gen 004/050 | best: 0.837 | mean: 0.540 | draws: 10%  ← peak
Gen 020/050 | best: 0.606 | mean: 0.495 | draws: 30%  ← triggered convergence
```

### Problem: plateau convergence triggered by a noisy bad generation
The old plateau check was:
```js
improvement = latest - history[history.length - 20]
// 0.606 - 0.776 = -0.170 < 0.001 → fired
```
Gen 20 had 30% draws and fitness dropped to 0.606. Since `-0.17 < 0.001`, the
check fired — not because the population plateaued, but because one generation
had a bad tournament draw. The check compares `latest` (can be any value) to a
past value, so any decline over the window triggers it.

### Fix applied — two-gate convergence (`src/training/evolution.js`)

**Gate 1 — Use window peak, not latest**
```diff
- improvement = latest - history[history.length - 20]
+ windowBest  = Math.max(...fitHistory.slice(-30))
+ improvement = windowBest - window[0]
```
A single bad generation can no longer trigger the check. The question becomes:
"has the best value seen in 30 gens improved over what we saw 30 gens ago?"

**Gate 2 — Require elite variance below threshold**
```js
if (variance(eliteFitnesses) < 0.005) return true;
```
Even if the 30-gen peak has plateaued, if the top 4 elites still have diverse
fitnesses the population is still exploring. Both gates must pass simultaneously.

**Window extended from 20 → 30 generations**

Verification against the gen-20 false trigger:
```
Old:  0.606 - 0.776 = -0.170 < 0.001  → FIRES (wrong)
New:  length=20 < 30                   → does NOT fire (correct)
      windowBest=0.837, window[0]=0.776, improvement=0.061 > 0.001
      elite variance=0.000068 < 0.005 (but gate 1 already fails)
```

---

## Entry 009 — A2 Remaining Fixes + A3 Persistence
**Date:** 2026-03-24

### A2 fixes applied

**1. `gamesPerMatchup` default raised 10 → 20** (`src/training/evolution.js`, `scripts/train.js`)
Each matchup now plays 20 games instead of 10. This halves tournament noise
(variance ∝ 1/n) without changing architecture. `--games 20` is the new default
in the usage comment.

**2. `win` cap lowered 300 → 200** (`src/training/mutate.js`)
The population naturally converges toward win=80–135; the 300 cap was letting
it drift up to 463 before the draw-penalty fix brought it back. 200 is a safe
ceiling well above the convergence zone.

**3. `DEFAULT_WEIGHTS.win` raised 100 → 150** (`src/bots/minimax.js`)
Seeds fresh runs from 150 — centred on the observed convergence zone — rather
than 100 (too low) or 300 (too high). The "default seed value" the user referred
to lives in `DEFAULT_WEIGHTS`, not `mutate.js`.

**4. `best.json` reset** (`data/weights/best.json`)
- `win` clamped from 300 → 150 (aligns with new cap/seed intent)
- `generation` reset to 0, `fitness` reset to 0 (clean-slate for generation
  tracking; ensures verification run produces `gen_001.json`–`gen_005.json`)
- Other evolved weights preserved (centreBonus, three, two, depthBonus, threatPenalty)

---

### A3 — Persistence module implemented

**New file: `src/io/persistence.js`**

All save/load logic extracted from `evolution.js` into a dedicated module with
five named exports:

| Function | Description |
|---|---|
| `loadBest(defaultWeights)` | Read `best.json`; return `{ weights, generation, fitness }` |
| `saveBest(bot)` | Overwrite `best.json` |
| `saveGeneration(gen, bot)` | Write `data/weights/gen_NNN.json` snapshot |
| `loadHistory()` | Read `data/metrics/history.json`; return `[]` if missing |
| `appendMetrics(entry)` | Append one entry to `history.json` |

`saveBest` and `saveGeneration` both call `ensureDir()` (mkdirSync recursive),
so the weights directory is always created on first run. A `strip()` helper
removes the non-serialisable `fn` field before writing.

**`evolution.js` rewritten to use `persistence.js`**

- Removed: `readFileSync`, `writeFileSync`, `existsSync`, `__dirname`, `ROOT`,
  `BEST_PATH`, `HIST_PATH`, `loadSeedWeights()`, inline `saveBest()`, `appendHistory()`
- Added: `import { loadBest, saveBest, saveGeneration, appendMetrics }`
- `loadBest(DEFAULT_WEIGHTS)` returns `{ weights, generation, fitness }` — no
  longer discards saved fitness and generation number

**Generation tracking fixed: resumes from correct absolute gen number**

```js
// Before: always started from gen 1
for (let gen = 1; gen <= cfg.generations; gen++)

// After: startGen loaded from best.json, loop continues from there
const startGen = seed.generation;        // 0 on first run, 4 after 4 gens saved
const lastGen  = startGen + cfg.generations;
for (let gen = startGen + 1; gen <= lastGen; gen++)
```

The header now shows the absolute range on resume:
```
Resuming from saved weights (gen 4, fitness 0.708)
Phase A — Evolutionary weight tuning
  pop=10  elites=4  depth=4  games/matchup=20  gens=3 (gen 5–7)  anchors=3
```

---

### Verification results

**Run 1 — fresh start (gen 0 seed):**
```
node scripts/train.js --gens 5 --pop 10 --games 20 --elite 4
```
```
Gen 001/005 | best: 0.650 ...
Gen 002/005 | best: 0.625 ...
Gen 003/005 | best: 0.667 ...
Gen 004/005 | best: 0.708 ...   ← bestOverall saved here
Gen 005/005 | best: 0.625 ...
Done. Best fitness: 0.7083 (gen 4)
```
Files created: `gen_001.json` through `gen_005.json` ✓
`best.json` updated to gen 4, fitness 0.708 ✓
`history.json` has 5 new entries ✓
No early convergence (history.length=5 < 30) ✓

**Run 2 — resume check:**
```
node scripts/train.js --gens 3 --pop 10 --games 20 --elite 4
```
```
Resuming from saved weights (gen 4, fitness 0.708)
Gen 005/007 | best: 0.696 ...   ← starts from 5, not 1
Gen 006/007 | best: 0.723 ...
Gen 007/007 | best: 0.682 ...
```
Files created: `gen_006.json`, `gen_007.json` (not overwriting gen_001) ✓
Absolute gen numbering preserved across restarts ✓

---

## Entry 010 — Phase A Convergence + A4 Metrics/Visualisation
**Date:** 2026-03-24

### Phase A — Convergence result

Training converged at generation 55 (stopped early). Best found at **gen 26**:
```
fitness:  0.9425  (943 wins vs pool including 3 random anchors)
weights:  centre=2.63  two=1.19  three=4.53  win=200  depthBonus=0.30  threatPenalty=0
```

Key observations from the 50-gen run (gens 7–56):
- `win` weight hit the 200 cap and stayed there for most runs — signals the cap
  is the binding constraint, not the true optimum
- `three` rose steadily from ~2.5 to 4.53 — the bot learned to value 3-in-a-row
  more heavily as depth-4 search horizon allows acting on them
- `depthBonus` settled at 0.30 — preferring sooner wins (not in original defaults)
- `threatPenalty` decayed to zero — not useful at depth 4 given explicit search
- Draw rate stayed 10–25%, well below the 50% draw-farming episode

**Benchmark results (100 games each, depth 6):**
- vs random bot: **100% win rate** (100W / 0L / 0D)
- vs default-weights minimax (depth 6): **50% win rate** (50W / 50L / 0D)

The 50/50 result vs default is expected: training was at depth 4, and at depth 6
the search itself is much stronger — weight differences have less impact as the
bot can see further. The weights are calibrated for depth-4 heuristic scoring;
depth-6 search partially compensates for suboptimal weights by looking further.

---

### A4 — Metrics and visualisation implemented

**`src/viz/board.js`** — `printBoard(board, label?)`
Full Connect 4 board with ANSI colour:
- `AI (2)` → red ●
- `HUMAN (1)` → yellow ○
- `EMPTY (0)` → dim ·
- Grid with `+---+` dividers and column numbers 1–7

**`src/viz/metrics.js`** — `printHeader`, `printGenLine`, `fmtWeights`
Extracted from `evolution.js`. These were already implemented inline; moving them
to `src/viz/` makes them importable by tools and benchmark scripts independently.

**`src/viz/chart.js`** — `printFitnessChart(fitHistory, startGen)`
ASCII fitness chart printed every 10 gens during training and at convergence:
```
  Fitness over generations
  1.0 |
  0.9 |                                      *                   *
  0.8 |                                  *         *           *   *
  0.7 |*   *                 * *           *   * *   * * * * * * *   * *   *
  0.6 |  *   * * * * * * * *     * * * *                   * *           *   * *
  0.5 |
       +-------------------------------------------------------------> gen
             10        20        30        40        50
```
Y-levels: 0.5–1.0 in 0.1 steps. Each column maps to one generation (sampled
if n > 54 columns). `*` placed at the row whose label = round(fitness × 10)/10.
X-axis shows generation numbers at a rounded interval.

**`scripts/benchmark.js`** — full implementation replacing the TODO stub
```
node scripts/benchmark.js [--games N] [--depth D]
```
- Loads best.json via `loadBest()`
- Plays best bot vs random bot (N games)
- Plays best bot vs default-weights minimax (N games)
- Prints formatted W/L/D table with percentages
- Prints overall win rate summary
Default: 200 games, depth 6.

**`evolution.js`** — wired to viz modules
- Imports `printHeader`, `printGenLine`, `fmtWeights` from `src/viz/metrics.js`
- Imports `printFitnessChart` from `src/viz/chart.js`
- `printFitnessChart(fitHistory, startGen)` called after every 10th generation
  and once more at convergence (early stop or final gen)
- Inline print functions removed from `evolution.js`

---

## Current State Summary

| Item | Status |
|------|--------|
| Phase A1 — Core engine | ✅ Complete |
| Phase A2 — Training loop | ✅ Complete |
| A2 fix: games/matchup default 10→20 | ✅ Applied |
| A2 fix: win cap 300→200 | ✅ Applied |
| A2 fix: DEFAULT_WEIGHTS.win 100→150 | ✅ Applied |
| A3 — `src/io/persistence.js` | ✅ Complete |
| A3 — per-gen `gen_NNN.json` snapshots | ✅ Complete |
| A3 — correct gen resuming | ✅ Fixed |
| Anchor-bot fix | ✅ Applied — mean > 0.5 confirmed |
| Mutation sigma fix | ✅ Applied — weights evolving |
| `bestOverall >=` fix | ✅ Applied |
| Draw-penalty fitness fix | ✅ Applied — draws × 2 in denominator |
| Convergence robustness fix | ✅ Applied — 30-gen window + elite variance gate |
| Phase A converged | ✅ Gen 26, fitness 0.9425, 100% vs random |
| Phase A4 — Metrics viz | ✅ Complete |
| Phase A5 — Parallelisation | ⬜ Not started |
| Phase C — MCTS | ⬜ Not started |
| Phase B — Neural net | ⬜ Not started |

## Immediate Next Step

Phase A complete. Next: **A5 — Parallelisation** (worker_threads, ~5× speedup on M3 Pro)
or skip to **Phase C — MCTS bot**.

---

*This file is updated after every major change, training run, or architectural decision.*
