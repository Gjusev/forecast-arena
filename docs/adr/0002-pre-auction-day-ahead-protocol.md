# ADR 0002: Pre-auction day-ahead protocol for electricity prices

## Status

Accepted (2026-11-06)

## Context

German day-ahead prices are auction results: the SDAC gate closes at 12:00 CET on
D-1 for all 24 delivery hours of day D. Any "forecast" of day D prices must only use
information published before the forecaster's origin. Since late 2025 the market also
has 15-minute products, creating two granularity regimes that must not be silently
merged.

## Decision

1. **Forecast origin: 10:00 CET on D-1** — safely before gate closure, so every
   admitted input is provably pre-auction.
2. **Benchmark granularity: hourly** day-ahead prices for the DE bidding zone,
   the long consistent history. The quarter-hourly era is documented as out of
   scope for the main benchmark; no merging of granularities.
3. **Two tracks:**
   - *Univariate* — all day-ahead prices published before the origin, i.e. delivery
     hours through D-1 23:00 (the D-1 auction closed D-2 12:00; its results are
     known before the origin even though some D-1 delivery hours have not yet
     occurred in wall-clock time). The 24 targets are D's delivery hours — the
     next 24 consecutive hourly slots after D-1 23:00.
   - *Multivariate* — adds calendar features and realized actuals (load,
     generation) with a conservative D-2 23:00 cutoff, plus pre-auction TSO
     day-ahead load/wind/solar forecasts for D where a vintage-correct source is
     available. Outcome variables of D and observed weather posing as forecast
     weather are forbidden.
4. Timezone Europe/Berlin with explicit DST handling; missing hours during DST
   transitions are expected and handled, not silently filled.

## Consequences

- Leakage review reduces to "input publication timestamp < 10:00 CET on D-1".
- Models forecast all 24 delivery hours of D; errors are reported per delivery
  hour and by peak/off-peak blocks, not by "steps ahead" as in the train experiment.
- Foundation models compete on the univariate track; LightGBM/XGBoost on both.
