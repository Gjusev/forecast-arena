<p align="center">
  <a href="https://huggingface.co/spaces/Gjusev/forecast-arena">
    <img src="assets/brand/banner.png" alt="AI vs Reality: eight forecasting models, two real German systems, every number published" width="100%">
  </a>
</p>

<p align="center">
  <a href="https://huggingface.co/spaces/Gjusev/forecast-arena"><b>Live demo</b></a> ·
  <a href="reports/01-train-delays.md">Train delays report</a> ·
  <a href="reports/02-electricity-prices.md">Electricity report</a> ·
  <a href="assets/video/forecast-arena.mp4">Watch the 33-second film</a>
</p>

<p align="center">
  <a href="https://github.com/Gjusev/forecast-arena/actions/workflows/ci.yaml"><img src="https://github.com/Gjusev/forecast-arena/actions/workflows/ci.yaml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/license-MIT-0b0b0b" alt="MIT license">
  <img src="https://img.shields.io/badge/python-3.11%20%7C%203.12-0b0b0b" alt="Python 3.11 | 3.12">
</p>

# forecast-arena

**Real data. Real predictions. Real results.** An open benchmark that tests
whether time series foundation models actually beat traditional methods on real,
messy operational data, with reproducible code, leakage-guarded protocols, and
the failures published next to the wins.

Vendors report wins on academic benchmarks. We re-test that claim on two systems
Germany runs on: **Deutsche Bahn train delays** and **day-ahead electricity prices**.

<p align="center">
  <a href="assets/video/forecast-arena.mp4">
    <img src="assets/video/preview.gif" alt="33-second motion summary: forecasts miss a 61-minute delay in Frankfurt, the train leaderboard is a dead heat, foundation models catch a negative-price Sunday and win on power prices, and forecast-based scheduling saves 40.2 euros a day" width="100%">
  </a>
  <br><sub>Click for the full-resolution MP4 (1080p, 33 s). Every number comes from <code>assets/video/story.json</code>, exported from the committed results.</sub>
</p>

## What we found

### 1. Trains: everyone misses the same disruption

<img src="assets/video/stills/01-trains-miss.png" alt="Frankfurt Hbf, 5 Feb 2026: reality reached 61 minutes average delay in the first hour while six models forecast between 1.5 and 7.1 minutes" width="100%">

The worst hour in the test window: Frankfurt (Main) Hbf, 5 Feb 2026. Average
arrival delay hit **61 min**; six models forecast **1.5 to 7.1 min**. Hourly
aggregates alone cannot see an incident coming, whichever model reads them.

### 2. Trains: a dead heat over 550 forecasts

<img src="assets/video/stills/02-trains-board.png" alt="Train delay leaderboard: foundation models 1.84 to 1.90 minutes MAE, gradient boosting 1.92 to 1.93, seasonal naive 2.76" width="100%">

MAE in minutes, 1 hour ahead, 5 hub stations × 110 rolling origins, vs **seasonal naive 2.76**:

| Model | MAE | Skill vs naive | 80%-interval coverage |
|---|---|---|---|
| Timestral 209M | **1.84** | +33.2% | 0.78 |
| Timestral 28M | 1.87 | +32.4% | 0.77 |
| Chronos-2 | 1.89 | +31.4% | 0.76 |
| TimesFM 3.0 | 1.90 | +31.4% | 0.79 |
| LightGBM | 1.92 | +30.7% | — |
| XGBoost | 1.93 | +30.2% | — |

Every serious model beats naive by ~30% (p < 1e-8), but the best foundation model
and laptop-trained gradient boosting are **0.07 minutes** apart.

### 3. Power: the models saw the free-power Sunday coming

<img src="assets/video/stills/03-power-catch.png" alt="Sunday 7 July 2024: 17 hours of negative day-ahead prices; Timestral 209M and LightGBM both forecast the dip below zero a day ahead" width="100%">

An illustrative solar Sunday (7 July 2024, chosen because it shows the mechanism
clearly): 17 hours below zero, forecast the morning before the auction. The
aggregate numbers below are the honest test.

### 4. Power: over 1,408 days, foundation models win

<img src="assets/video/stills/04-power-board.png" alt="Power leaderboard: foundation models reduce error 31 to 33 percent vs naive, gradient boosting 17 to 19 percent; negative-price F1 0.57 vs 0.23" width="100%">

MAE €/MWh pooled over all 24 delivery hours, 1,408 daily pre-auction origins (2021–2026), vs **seasonal naive 28.20**:

| Model | MAE | Skill vs naive | Neg-price F1 |
|---|---|---|---|
| Chronos-2 | **19.27** | +33.1% | 0.50 |
| Timestral 209M | 19.53 | +32.4% | **0.57** |
| TimesFM 3.0 | 19.82 | +31.2% | 0.48 |
| Timestral 28M | 19.82 | +31.6% | 0.53 |
| XGBoost | 23.48 | +19.1% | 0.23 |
| LightGBM | 24.14 | +17.2% | 0.19 |

The opposite of the delays result: foundation models clearly beat gradient
boosting (+31–33% vs +17–19%), and GBMs are nearly blind to negative-price hours.

### 5. Does it pay? On wholesale prices, yes

<img src="assets/video/stills/05-money.png" alt="Scheduling 4 MWh a day on Chronos-2 forecasts costs 196.6 euros a day vs 236.7 for fixed midday hours, a saving of 40.2 euros a day and 74 percent of the perfect-foresight saving" width="100%">

Scheduling 4 MWh of flexible daily load on the best model's forecast saved
**40.2 €/day (−17%)** vs a fixed midday schedule, capturing **74% of the
perfect-foresight saving** (wholesale costs only, not household bills).

Publication charts: [`assets/charts/`](assets/charts/) · full reports: [`reports/`](reports/).

## Explore it yourself

The [live demo on Hugging Face Spaces](https://huggingface.co/spaces/Gjusev/forecast-arena)
reads the same committed result files:

- **Replay a forecast.** Scrub through every forecast origin, pick your
  contenders, call the winner, then reveal what really happened.
- **Leaderboard.** Rank by error or skill, per horizon, with runtimes.
- **Head to head.** Any two models, every forecast as one dot, win rate.
- **Does it pay?** Cumulative scheduling savings per model against perfect foresight.
- **Live.** Every day at 00:45 CET the workflow publishes forecasts for the *next*
  day's auction, committed before that auction runs (12:00 CET). Once the day's
  prices are out, the same workflow scores them: a rolling, tamper-evident
  leaderboard. See `live/` and `scripts/live_forecast.py`.

```bash
uv run --extra dashboard python dashboard/app.py   # -> http://localhost:7860
```

## Experiments

| # | Experiment | Question | Data |
|---|---|---|---|
| 1 | [Train delays](experiments/01-train-delays/) | Can Timestral-209M predict Deutsche Bahn disruption levels hours ahead? | 5 major stations, 2024-07 → 2026-10, ~5.7M arrivals |
| 2 | [Electricity prices](experiments/02-electricity-prices/) | Can small foundation models predict negative prices and spikes in the German day-ahead market? | DE-LU hourly day-ahead prices, 2018-10 → today |

## Models

| Family | Models |
|---|---|
| Foundation (zero-shot) | Mistral **Timestral 28M / 209M**, Amazon **Chronos-2**, Google **TimesFM 3.0** |
| Traditional ML | **LightGBM**, **XGBoost** (lag + calendar features, retrained per origin) |
| Statistical baselines | **Seasonal naive (24h)**, **hour-of-week climatology** |

Every model receives *identical* information at every forecast origin; see the
methodology below.

## Methodology (short version)

- **Rolling-origin evaluation** — chronological splits, no shuffling, identical
  origins and inputs for every model.
- **Leakage guards by construction** — models only ever receive history
  truncated at the origin ([ADR-0001](docs/adr/0001-completed-hour-forecasting-protocol.md),
  [ADR-0002](docs/adr/0002-pre-auction-day-ahead-protocol.md)).
- **Pre-registered event thresholds** — disruption / negative-price / spike
  thresholds frozen on training data before holdout evaluation.
- **Honest metrics** — MAE, RMSE, MASE vs seasonal naive, sMAPE where valid
  (never MAPE on prices), interval coverage, detection precision/recall,
  inference runtime.
- **Significance** — Diebold-Mariano tests vs the best baseline with a
  multiple-testing caveat stated.

## Quickstart

```bash
# Python 3.11+ via uv
uv sync --group dev --extra ml --extra foundation

# fetch data + build aggregates
uv run arena build-data 01
uv run arena build-data 02

# run benchmarks (smoke -> pilot -> full)
uv run --extra ml --extra foundation arena run 01 --tier smoke
uv run --extra ml --extra foundation arena run 01 --tier pilot
uv run --extra ml --extra foundation arena run 02 --tier smoke

# tests (no model downloads)
uv run pytest tests -q
```

## Brand and media

| Asset | File |
|---|---|
| Logo mark (SVG / PNG) | [`assets/brand/mark.svg`](assets/brand/mark.svg), [`mark-512.png`](assets/brand/mark-512.png) |
| Banner / social preview (2:1) | [`assets/brand/banner.png`](assets/brand/banner.png) |
| Motion film (1080p MP4, GIF preview, stills) | [`assets/video/`](assets/video/) |
| Storyboard | [`assets/video/STORYBOARD.md`](assets/video/STORYBOARD.md) |

The mark is the benchmark's core idea: history runs up to the **forecast origin**
(the yellow bar), then splits into the forecast (dotted, signal yellow) and
reality (paper white). The film is deterministic SVG rendered frame by frame:

```bash
uv run python scripts/export_story_data.py                     # numbers from committed results
uv run --with playwright python scripts/render_motion.py all   # needs Chrome + ffmpeg
```

## Repository layout

```
experiments/        one folder per experiment (config + results + reports)
src/forecast_arena/
  data/             dataset loaders and panel builders
  models/           forecaster interface + adapters (baselines, GBMs, foundation)
  evaluation/       metrics, protocol, runner, analysis, simulation
  visualization/    publication charts
dashboard/          Gradio app over cached results (deployed as the HF Space)
assets/             brand, motion film + storyboard, publication charts
docs/adr/           accepted methodology decisions
reports/            technical reports + LinkedIn drafts (English)
```

## Data sources & licenses

| Data | Source | License |
|---|---|---|
| DB train delays | [piebro/deutsche-bahn-data](https://huggingface.co/datasets/piebro/deutsche-bahn-data) (aggregated Deutsche Bahn timetable data) | CC-BY-4.0 |
| Day-ahead prices | [SMARD](https://www.smard.de) (Bundesnetzagentur), filter 4169 | dl-de/by-2-0 |

This repository ships download scripts and small derived aggregates only —
raw datasets stay with their publishers under their terms.

## Limitations (the honest part)

- Train-delay forecasts are **operational-planning forecasts** on completed
  hourly aggregates, not individual-train predictions (real dispatch systems
  see en-route trains; our models do not — results are a lower bound).
- Electricity forecasts respect the day-ahead auction clock; they compete
  with professional traders who see more than hourly public data.
- Benchmarks run on consumer hardware (CPU); runtimes are reported per model
  but wall-clock comparability across hardware is approximate.

## License

MIT for code. See [LICENSE](LICENSE). Datasets keep their upstream licenses.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — methodology integrity first.
