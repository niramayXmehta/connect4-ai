# Connect4 AI — Evolutionary Training System

A multi-phase project to build and train the strongest possible Connect 4 bot,
starting with evolutionary weight tuning (Phase A), then Monte Carlo Tree Search
(Phase C), then neural network reinforcement learning (Phase B).

## Quick start

```bash
npm install
node scripts/train.js          # run evolutionary training
node scripts/simulate.js       # run a batch of games between two bots
node scripts/benchmark.js      # benchmark current best bot vs baseline
```

## Project phases

| Phase | Method | Status |
|-------|--------|--------|
| A | Evolutionary weight tuning | in progress |
| C | Monte Carlo Tree Search | planned |
| B | Neural network (PyTorch/Python) | planned |

## Directory structure

```
connect4-ai/
├── README.md
├── docs/                        # design documents and thinking
│   ├── ARCHITECTURE.md          # system design and data flow
│   ├── PHASE_A.md               # evolutionary algorithm spec
│   ├── PHASE_C.md               # MCTS spec
│   ├── PHASE_B.md               # neural net spec
│   └── METRICS.md               # what we measure and why
├── src/
│   ├── game/                    # pure game logic, no AI, no UI
│   │   ├── board.js             # board state, place, unplace, helpers
│   │   ├── rules.js             # checkWin, isFull, validCols
│   │   └── constants.js         # ROWS, COLS, HUMAN, AI, default WIN
│   ├── bots/                    # bot implementations
│   │   ├── minimax.js           # minimax + alpha-beta, reads weights
│   │   ├── mcts.js              # MCTS bot (phase C)
│   │   └── random.js            # random bot, used as baseline
│   ├── training/                # training loops
│   │   ├── evolution.js         # evolutionary algorithm (phase A)
│   │   ├── mutate.js            # weight mutation logic
│   │   └── fitness.js           # fitness evaluation (win rate vs pool)
│   ├── simulation/              # runs games between bots
│   │   ├── runner.js            # plays N games, returns results
│   │   └── tournament.js        # round-robin tournament between a pool
│   └── viz/                     # terminal visualisation
│       ├── board.js             # prints board to terminal
│       ├── metrics.js           # prints training metrics table
│       └── chart.js             # ASCII charts for win rate over time
├── data/
│   ├── weights/                 # saved bot weight files (JSON)
│   │   └── best.json            # current best weights
│   ├── logs/                    # per-run logs
│   └── metrics/                 # training metrics history (JSON)
├── scripts/                     # entry points
│   ├── train.js                 # run evolutionary training loop
│   ├── simulate.js              # simulate games between two saved bots
│   └── benchmark.js             # test a bot against baseline and random
└── package.json
```

## Bot weight format

Each bot is defined by a weights object:

```json
{
  "id": "bot_0042",
  "generation": 12,
  "weights": {
    "centreBonus": 3,
    "three": 5,
    "two": 2,
    "win": 100,
    "terminalWin": 1000000
  },
  "fitness": 0.84,
  "gamesPlayed": 1200,
  "wins": 1008,
  "losses": 144,
  "draws": 48
}
```

## Saved data persistence

- `data/weights/best.json` — best bot from all training so far
- `data/weights/gen_NNN.json` — snapshot of best bot each generation
- `data/metrics/history.json` — full training history for graphing
- Training resumes from the last saved generation automatically
