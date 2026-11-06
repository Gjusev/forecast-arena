# Experiment 02 — German day-ahead electricity prices

**Working title:** *Can a tiny AI model predict negative electricity prices in Germany?*

## Research question

Can zero-shot foundation models forecast the German day-ahead auction —
including negative-price hours and extreme spikes — well enough to schedule
flexible consumption cheaper than simple heuristics?

## Dataset

[SMARD](https://www.smard.de) (Bundesnetzagentur), filter 4169 — hourly
day-ahead prices for the DE(LU) bidding zone, 2018-10 → present, license
dl-de/by-2-0, no API token. Benchmark window 2021-01 → 2026-11
(≈ 50,800 hourly slots, 48 nulls, ~3.6% negative-price hours).
Cross-checked against the energy-charts v2 price API.

Rejected alternatives (documented): `mt0rm0/opsdata` (no German prices, DE
features end 2020-10), `hsilvosa/entsoe-day-ahead` (unmapped ENTSO-E license
terms — cross-check use only).

## Protocol — pre-auction day-ahead (ADR-0002)

Forecast origin = **10:00 CET on D-1** (before the 12:00 SDAC gate closure).
Information set:

- **Univariate track:** all day-ahead prices published before the origin =
  delivery hours through D-1 23:00 (the D-1 auction closed D-2 12:00)
- **Multivariate track (GBMs):** + calendar; realized actuals strictly
  through D-2 23:00. Day-ahead TSO forecast series are excluded unless a
  vintage-correct source is verified (energy-charts forecasts are
  *current*-vintage → post-hoc reforecasts → leakage as inputs)
- Targets: all 24 delivery hours of D; `h` in the results **is** the delivery
  hour. No silent merging with the post-2025 quarter-hourly market regime.
- Spike threshold: training-period P99 of prices; negative price = < 0 €/MWh
  — both frozen before holdout evaluation

## Business simulation

4 MWh of flexible consumption placed in the predicted-cheapest 4 hours of
each delivery day; realized cost at actual auction prices. Strategies:
oracle (perfect foresight), model-scheduled, fixed midday (10:00–13:00),
yesterday's cheapest hours. Wholesale market costs only — **not** household
bill savings.

## Results

In `results/` — verified numbers only in the
[technical report](../../reports/02-electricity-prices.md).

## Reproduce

```bash
uv sync --group dev --extra ml --extra foundation
uv run arena build-data 02
uv run --extra ml --extra foundation arena run 02 --tier smoke
uv run --extra ml --extra foundation arena run 02 --tier pilot
uv run --extra ml --extra foundation arena run 02 --tier full
uv run python scripts/make_report_assets.py full
```

## Limitations

- Hourly day-ahead product only; the 15-minute regime (since late 2025) is
  out of scope for the main benchmark.
- Professional forecasters see order books, plant outages, and cross-border
  flows we do not; our models see public hourly data only.
- 2021–2026 spans structural price-level shifts; seasonal-naive and
  climatology baselines are honest victims of that nonstationarity.
