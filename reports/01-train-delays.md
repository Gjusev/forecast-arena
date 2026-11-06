# Technical Report 01 — Can foundation models predict German train delays?

*Experiment: train-delays · full tier · 110 rolling origins · executed 2026-11-06
· all numbers generated from
[`results/report_assets_full/`](../experiments/01-train-delays/results/report_assets_full/)
— nothing in this report is hand-computed.*

## Research question

Zero-shot time series foundation models are marketed as forecasting
generalists. Do they beat classical methods at predicting station-level
disruption at Germany's five largest railway hubs, hours ahead — and by how
much, at what compute cost, with what failure modes?

## Dataset

**Source:** [piebro/deutsche-bahn-data](https://huggingface.co/datasets/piebro/deutsche-bahn-data)
(CC-BY-4.0) — finalized per-stop records aggregated from Deutsche Bahn
timetable data, monthly parquet files, 2024-07 → 2026-10.

- ~5.7M arrivals across the 5 stations (all rail services; bus replacements
  excluded). Station identity resolved from the data itself (Berlin
  Hauptbahnhof alone spans three EVA codes).
- Mean average delay per station: Hamburg 4.3 min, Berlin 4.3 min, Frankfurt
  5.5 min, München 6.1 min, Köln 7.1 min.
- Timestamps verified as Berlin wall clock (DST spring day has no 02:00).

## Protocol

Completed-hour protocol ([ADR-0001](../docs/adr/0001-completed-hour-forecasting-protocol.md)):
forecast origin = end of the last completed hour; inputs = hourly aggregates
of completed hours + calendar only. This is an *operational-planning*
forecast — no en-route information exists in any model input.

- Targets: average arrival delay (primary, minutes) and delayed arrivals per
  hour >5 min (secondary) at h = 1, 3, 6, 24 steps.
- 110 rolling origins (~weekly cadence, 167-hour phase rotation so short
  horizons cover all wall-clock hours), 5 stations × 2 targets = 10 series.
- Disruption-hour threshold per station: P90 of the training-period delayed
  count — **frozen before holdout evaluation**.
- Missing no-arrival hours imputed with the series' own hour-of-week mean
  (data ≤ origin), identically for every model.
- Statistical claims: Diebold-Mariano tests vs seasonal naive, |error| loss,
  HAC variance; 28 model-horizon tests → multiple-testing caveat applies.

## Models

Eight models under identical inputs: Timestral 28M/209M (zero-shot),
Chronos-2 (zero-shot), TimesFM 3.0 (zero-shot), LightGBM and XGBoost (global
lag/calendar models, retrained per origin on data ≤ origin), seasonal naive
(24h), hour-of-week climatology. Run on CPU (see manifest for versions).

## Results

### Primary target — average arrival delay (minutes, MAE, pooled stations)

| Model | h=1 | h=3 | h=6 | h=24 |
|---|---|---|---|---|
| Timestral 209M | **1.84** | **2.20** | 2.38 | 2.11 |
| Timestral 28M | 1.87 | 2.24 | 2.40 | 2.14 |
| Chronos-2 | 1.89 | 2.22 | 2.36 | **2.08** |
| TimesFM 3.0 | 1.90 | **2.20** | **2.31** | 2.10 |
| LightGBM | 1.92 | 2.35 | 2.58 | 2.10 |
| XGBoost | 1.93 | 2.36 | 2.58 | 2.13 |
| Seasonal naive (24h) | 2.76 | 3.13 | 3.79 | 2.71 |
| Hour-of-week climatology | 3.73 | 4.42 | 3.96 | 3.17 |

Skill vs seasonal naive at h=1: **+30% to +33%** for every serious model —
foundation models and gradient boosting alike. The spread between the best
foundation model and the best GBM at h=1 is 0.08 minutes (~5 s of average
delay). At h=24 the four families converge within 0.05 min.

On the secondary target (delayed arrivals per hour) the pattern repeats:
+41.5% to +42.7% skill at h=1 across all six serious models, decaying to
+21–24% at h=24.

### Statistical significance

Diebold-Mariano vs seasonal naive at h=1: every model improves on the
baseline with p < 1e-8 (best: Timestral 209M, stat −6.72, p ≈ 1.8e-11).
With 28 tests, all results survive any multiple-comparison correction.

### Interval calibration (nominal 80%)

Foundation models: 0.74–0.82 empirical coverage — remarkably well
calibrated out of the box. Seasonal naive (residual-quantile intervals):
0.70–0.76, slightly narrow.

### Compute cost (110 origins × 10 series, CPU)

| Model | Seconds | vs naive |
|---|---|---|
| Seasonal naive | 0.1 | 1× |
| Climatology | ~0 | — |
| Timestral 28M | 34 | 342× |
| XGBoost | 43 | 431× |
| LightGBM | 47 | 474× |
| Chronos-2 | 76 | 755× |
| Timestral 209M | 187 | 1,873× |
| TimesFM 3.0 | 337 | 3,369× |

The 3,400× compute spread between the cheapest and most expensive model buys
≈0.06 min of MAE on the primary target.

## Failure analysis

**The disruption day nobody predicted.** On 2026-02-05, Frankfurt (Main) Hbf
average delay spiked above 60 minutes at midday. All eight models — including
all four foundation models — forecast a flat 5–10 minute day
([chart](../assets/charts/actual_vs_pred_avg_delay_min_Frankfurt(Main)Hbf_2026-02-05.png)).
This is the completed-hour protocol's honest limit: a disruption that emerges
within the day is invisible to models that only see completed hourly
aggregates. RMSE tells the story per station: Berlin RMSE 1.65–1.85 min at
h=1 (calm station) vs Frankfurt 5.6–6.0 min (spike-driven), while MAEs differ
by only ~0.9 min.

**Disruption detection (avg-delay P90 events, pooled h=1–24):** precision
0.33–1.0 and recall 0.13–0.5 depending on station and model (per-station
tables in `events.md`). Models are conservative: high precision, low recall —
they flag few disruption hours and miss most of them. Frankfurt is the only
station with enough events (23–24 in the evaluation window) for stable
estimates; there, Chronos-2 reaches precision 0.65 / recall 0.48 at h=1.

**Scale does not buy accuracy here.** Timestral 209M beats its 28M sibling by
0.02–0.03 min MAE (within noise), while costing 5.5× the inference time.

## Limitations

1. Finalized records only: real dispatch systems see en-route trains; our
   models cannot. Results are a lower bound on operational usefulness.
2. Five hubs, 28 months, one country.
3. Delay for on-time trains is encoded as 0 (absence of a change message) —
   the standard reading of this dataset, but it flattens early/late noise.
4. Hourly aggregates lose train-level structure entirely; the task is
   disruption-level planning, not trip planning.

## Reproduction

```bash
uv sync --group dev --extra ml --extra foundation
uv run arena build-data 01
uv run --extra ml --extra foundation arena run 01 --tier full
uv run python scripts/make_report_assets.py full
uv run python scripts/make_charts.py delays
```

Runtime ≈ 13 min of model compute on CPU plus ~2 min data build (after the
one-time ~1.7 GB dataset download).
