# CONTEXT.md — Glossary

The glossary for `forecast-arena`. Terms only — no implementation details, no specs.
When a term is resolved or sharpened, update it here immediately.

## Project & Publication

- **forecast-arena** — the repository name (local directory and published GitHub repo).
- **AI vs Reality** — the project *brand*: README title, dashboard header, publication
  copy. Tagline: "Real Data. Real Predictions. Real Results." Not the repo name.
- License: MIT for code. Datasets keep their upstream terms; we ship download scripts
  and small derived aggregates only.

## Train-Delays Experiment

- **Completed Hour** — an hour of station operations whose trains' outcomes (arrival
  times, cancellations) are all finalized. Knowable only after the hour ends.
- **Hourly Aggregate** — a per-station, per-hour summary of completed arrivals
  (e.g. average arrival delay in minutes). The unit of both input and target series.
- **Forecast Origin** — the end of the last completed hour; the timestamp at which
  a forecast is "made". Everything after it is the future.
- **Horizon** — how far ahead of the Forecast Origin a target hour lies (1h, 3h,
  6h, 24h).
- **Operational-Planning Forecast** — what this experiment actually produces:
  disruption levels hours ahead from completed observations. Explicitly *not*
  individual-train prediction.
- **Primary Target** — average arrival delay (minutes), the headline series.
- **Secondary Target** — delayed-arrival count (>5 min) per hour; feeds disruption
  detection. The remaining three mission series (% delayed, total delay minutes,
  cancellation rate) are built and shipped as data, not fully benchmarked.

## Electricity-Prices Experiment

- **D / D-1 / D-2** — the delivery day; the day before it (auction + forecast-origin
  day, whose day-ahead *prices* are already published at the origin); the day before
  that (last day with realized actuals under the conservative feature cutoff).
- **Pre-Auction Origin** — 10:00 CET on D-1; the moment the forecast is "made".
- **Delivery Hour** — one of the 24 hourly slots of D being predicted. Errors are
  reported per delivery hour / peak-off-peak block, not per step-ahead.
- **Univariate Track** — models see day-ahead prices through D-2 only.
- **Multivariate Track** — adds pre-auction TSO load/wind/solar forecasts for D
  and calendar features. Outcome variables (actual load, generation, observed
  weather of D) are forbidden.

## Judging Results (both experiments)

- **Headline Criterion** — MASE vs seasonal-naive on the primary target, per
  horizon / delivery-hour block. Statistical claims via Diebold-Mariano tests
  against the best baseline, with multiple-testing caveat stated.
- **Disruption Hour** — an hour whose delayed-arrival count exceeds that station's
  P90, computed on training data only and frozen before holdout evaluation.
- **Negative-Price Hour** — day-ahead price < 0 EUR/MWh (definition is natural,
  nothing to tune).
- **Spike Hour** — day-ahead price ≥ the training-period P99 of prices; frozen
  before holdout evaluation.

