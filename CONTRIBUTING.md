# Contributing to forecast-arena

Thanks for your interest! This project benchmarks forecasting models against
real world data — methodological integrity matters more than leaderboard
placement.

## Ground rules

1. **No leakage.** Every feature available to any model must have been
   knowable at the forecast origin. Read
   [docs/adr/0001](docs/adr/0001-completed-hour-forecasting-protocol.md) and
   [docs/adr/0002](docs/adr/0002-pre-auction-day-ahead-protocol.md) first.
2. **No fabricated results.** Never report numbers that were not produced by a
   committed, reproducible run. Failed runs are recorded, not hidden.
3. **All models get identical inputs.** If a preprocessing step helps one
   model, it helps all of them.

## Development setup

```bash
git clone https://github.com/Gjusev/forecast-arena.git
cd forecast-arena
uv sync --group dev --extra ml --extra foundation
uv run pytest tests -q          # fast tests, no model downloads
uv run ruff check src tests
```

## Adding a model

1. Implement a `Forecaster` (see `src/forecast_arena/models/base.py`) —
   `prepare()` for per-origin training, `forecast()` per series.
2. Register it in `src/forecast_arena/experiment.py::REGISTRY`.
3. Add a fast unit test with synthetic data; live tests are opt-in via
   `ARENA_LIVE_TESTS=1` and never run in CI.

## Adding an experiment

1. New folder under `experiments/` with `config.yaml` + `README.md`.
2. Add a panel builder in `src/forecast_arena/data/panels.py` if the data
   shape is new; reuse the evaluation engine untouched.
3. Pre-register event thresholds on train data only before evaluating the
   holdout.

## Pull requests

- Keep diffs minimal; explain methodology changes in the PR body.
- New analysis code must come with a test or a runnable check.
- CI must pass (ruff + pytest).
