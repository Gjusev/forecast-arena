# forecast-arena — AI vs Reality

> **Real Data. Real Predictions. Real Results.**

An open benchmark that tests whether time series foundation models actually
outperform traditional methods on real world forecasting problems — with
reproducible code, honest protocols, and published failures alongside wins.

## The question

**"Can modern AI forecasting models beat classical methods on real, messy
operational data?"** Vendors report wins on academic benchmarks. We re-test
that claim on two problems Germany runs on: trains and electricity.

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

Every model receives *identical* information at every forecast origin —
see the methodology below.

## Headline results

🚧 Benchmarks are executing now. Results land here (with charts) once the
pilot and full runs complete, each traceable to a committed predictions file.
No numbers are shown that a reader cannot reproduce.

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

## Dashboard

```bash
uv run --extra dashboard python dashboard/app.py
# -> http://localhost:7860
```

Also deployed on Hugging Face Spaces (link added after publication).

## Repository layout

```
experiments/        one folder per experiment (config + results + reports)
src/forecast_arena/
  data/             dataset loaders and panel builders
  models/           forecaster interface + adapters (baselines, GBMs, foundation)
  evaluation/       metrics, protocol, runner, analysis, simulation
  visualization/    publication charts
dashboard/          Gradio app over cached results
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
