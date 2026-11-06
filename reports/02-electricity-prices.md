# Technical Report 02 — Can models predict negative electricity prices in Germany?

*Experiment: electricity · full tier · 1,408 daily origins · executed 2026-11-06
· all numbers generated from
[`results/report_assets_full/`](../experiments/02-electricity-prices/results/report_assets_full/)
— nothing in this report is hand-computed.*

## Research question

Can zero-shot foundation models forecast the German day-ahead auction —
including negative-price hours — accurately enough to schedule flexible
consumption cheaper than simple heuristics, under a strictly pre-auction
information protocol?

## Dataset

**Source:** SMARD (Bundesnetzagentur), filter 4169 — hourly day-ahead prices
for the DE-LU bidding zone, license dl-de/by-2-0, no API token, fetched via
the public JSON API (71,065 hourly slots 2018-10 → 2026-11, 48 nulls,
cross-checked against the energy-charts v2 API). Benchmark window 2021-01 →
2026-11: 50,832 hourly slots, 1,793 negative-price hours (3.5%).

Rejected alternatives (documented): `mt0rm0/opsdata` (no German prices, DE
features end 2020-10), `hsilvosa/entsoe-day-ahead` (unmapped ENTSO-E license
terms — used neither), energy-charts forecasts (current-vintage post-hoc
reforecasts → would leak; excluded as features by design).

## Protocol

Pre-auction day-ahead protocol ([ADR-0002](../docs/adr/0002-pre-auction-day-ahead-protocol.md)):
forecast origin = 10:00 CET on D-1 (before the 12:00 SDAC gate closure).
Univariate track: all day-ahead prices published before the origin — delivery
hours through D-1 23:00 (D-1's auction closed D-2 12:00). Targets: all 24
delivery hours of D. The 24h-lag seasonal naive is therefore a *strong,
honest* baseline — it knows D-1's published prices, exactly as a real
forecaster would.

- 1,408 daily origins (Oct 2022 → Nov 2026 after the 2-year minimum history).
- GBMs (multivariate track): calendar + price lags/rollings with the same
  pre-auction cutoff; refit weekly.
- Event thresholds frozen on training data only: negative price = < 0 €/MWh
  (natural definition); spike = training-period P99 = 593.1 €/MWh.
- DST: origins and targets live on true Berlin wall-clock slots (25-hour
  fall-back days occur in the data and are handled by the union grid).

## Results

### Price accuracy (MAE €/MWh, pooled over all 24 delivery hours, 1,408 days)

| Model | MAE | Skill vs naive | 80% coverage |
|---|---|---|---|
| Chronos-2 | **19.27** | **+33.1%** | 0.77 |
| Timestral 209M | 19.53 | +32.4% | 0.78 |
| TimesFM 3.0 | 19.82 | +31.2% | 0.80 |
| Timestral 28M | 19.82 | +31.6% | 0.77 |
| XGBoost | 23.48 | +19.1% | — |
| LightGBM | 24.14 | +17.2% | — |
| Seasonal naive (24h) | 28.20 | 0 | 0.63 |
| Hour-of-week climatology | 46.11 | −72.9% | — |

Unlike the train-delays experiment, foundation models **clearly** beat
gradient boosting here (+31–33% vs +17–19%; ≈4.5 €/MWh gap). Zero-shot
transfer survives an extreme nonstationary market — the window contains both
the 2022–23 energy-crisis prices and the 2024–26 renewable-collapse regime
with frequent negatives.

### Negative-price detection (1,793 negative delivery hours)

| Model | Precision | Recall | F1 |
|---|---|---|---|
| Timestral 209M | 0.673 | 0.490 | **0.567** |
| Timestral 28M | 0.702 | 0.428 | 0.532 |
| Chronos-2 | 0.732 | 0.377 | 0.498 |
| TimesFM 3.0 | 0.715 | 0.358 | 0.477 |
| Seasonal naive | 0.450 | 0.456 | 0.453 |
| XGBoost | 0.629 | 0.142 | 0.231 |
| LightGBM | 0.580 | 0.115 | 0.193 |

Foundation models detect negative hours at F1 ≈ 0.5–0.57; GBMs are nearly
blind (F1 ≤ 0.23) — they rarely predict negatives at all. All models are
conservative: precision 0.6–0.73, recall 0.36–0.49.

**Spikes (honest null result):** the pre-registered spike threshold — P99 of
training prices = 593 €/MWh, frozen before evaluation — produces **zero spike
hours in the test window**: the threshold is calibrated to the 2021–22 crisis
training period, and 2023–26 prices, while volatile, stay below it. We report
this as-is rather than re-tuning the threshold post hoc; the meaningful
extreme-event metric in this window is negative-price detection.

### Business simulation (4 MWh flexible load per day, 1,402 days)

Place 4 MWh in the predicted-cheapest 4 hours of each delivery day; realized
cost at actual auction prices. Scheduler = Chronos-2 (best MAE).

| Strategy | Mean cost €/day |
|---|---|
| Fixed midday (10:00–13:00) | 236.7 |
| **Model-scheduled** | **196.6** |
| Oracle (perfect foresight) | 182.8 |

- **Saving vs fixed midday: 40.2 €/day (−17.0%)**
- **Regret vs oracle: 13.8 €/day — the model captures 74.4% of the
  theoretically available saving**
- Wholesale market costs only. This is *not* a household bill estimate:
  retail contracts, taxes, levies and grid fees change the economics
  completely.

### Compute cost (1,408 origins, CPU)

Seasonal naive ~0 s, climatology ~0 s, Timestral-28M 47 s, Chronos-2 99 s,
Timestral-209M 236 s, LightGBM 194 s, XGBoost 244 s, TimesFM 528 s.

## Failure analysis

- **Coverage of the naive baseline collapses (0.63)** — its residual-quantile
  intervals, calibrated on one regime, miss the next. Foundation models stay
  at 0.77–0.80.
- **GBM negative-blindness**: lag features make "yesterday was negative" the
  dominant signal; the trees rarely cross zero. This is a textbook case of
  recursive multi-step prediction regressing to the mean.
- **Climatology (−73%)**: the 2021–26 price-level shifts are lethal to any
  static seasonal mean — an honest control that the benchmark punishes
  laziness.

## Limitations

1. Public hourly data only — professional traders see order books, outages,
   and cross-border flows; this is a public-information benchmark, not a
   trading desk.
2. Hourly product only; the 15-minute regime since late 2025 is out of scope.
3. Univariate track for foundation models (no covariates); GBMs got the same
   information plus calendar. Vintage-correct load/renewables forecasts were
   not available license-clean, so the multivariate track stayed lean.
4. Scheduling assumes perfectly flexible load with no ramp constraints.

## Reproduction

```bash
uv sync --group dev --extra ml --extra foundation
uv run arena build-data 02
uv run --extra ml --extra foundation arena run 02 --tier full
uv run python scripts/make_report_assets.py full
uv run python scripts/make_charts.py electricity
```

Runtime ≈ 25 min of model compute on CPU after the one-time SMARD fetch
(~423 API calls, a few minutes).
