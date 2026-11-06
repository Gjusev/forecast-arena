# Experiment 04 — German renewable generation (energy-charts)

**Working title:** *Can a small AI model follow the wind and the sun?*

## Research question

Can zero-shot foundation models forecast German wind + solar generation
day-ahead (next 24 h) well enough to run a battery/dispatch business case —
and to detect forecast-error spikes — better than seasonal persistence?

## Dataset

[Fraunhofer ISE energy-charts](https://energy-charts.info) `public_power`
API, bidding zone **DE-LU**: 15-minute net generation (MW) for wind onshore,
wind offshore and solar, license **CC BY 4.0** (attribution rides in every
API payload and is preserved in the cache). Fetched 2019-01-01 -> present in
yearly chunks and aggregated to **hourly mean MW**; `wind_total` = onshore +
offshore summed at 15-min level. Benchmark window 2019-01-01 onward
(post zone change DE-AT-LU -> DE-LU, 2018-10).

## Protocol

Rolling daily origins, horizon 24 h, eval horizons h = 1, 3, 6, 24.
Forecast origin = 00:00 **Europe/Berlin** wall clock; every model sees only
history strictly before the origin plus the calendar (hour-of-week, DST-
correct). No weather or generation forecasts as inputs — zero-shot vs
trained-on-past only. Headline metric MASE/MAE skill vs `seasonal_naive_24h`;
thresholds (P99 forecast-error spike, frozen on train only) per the arena
pre-registration convention.

## Data caveats

- energy-charts revises recent 15-min values; the cache freezes one snapshot
  at refresh time and scores it as-is.
- Hours with no 15-min values stay null and are imputed hour-of-week
  (identically for every model) by the shared runner.

## Results

In `results/` — smoke tier complete (3 models x 2 series x 3 origins x 24 h,
all y_true finite): on `wind_offshore` LightGBM (+78% MAE skill at h=1) and
Chronos-2 (+57%) both beat seasonal-naive clearly; `solar` needs an
hour-filtered skill metric (night hours are exactly 0, so seasonal-naive is
unsurpassable and `skill_vs_baseline_pct` is undefined there - flagged to the
shared runner as a needed zero-guard). Pilot/full pending.
