# Dataset research for experiments 03+ (2026-11-06)

Four parallel research passes (energy, transport, weather, dataset hubs), all
licenses and access paths verified live the same day. Combined with the arena's
hard criteria: open license permitting derived aggregates, hourly-or-denser
granularity, leakage-clean forecast origins, programmatic download.

## Combined ranking

| # | Candidate | Domain | License | Coverage | Access | Fit |
|---|-----------|--------|---------|----------|--------|-----|
| 1 | DWD hourly station observations (temp, wind, gust, precip, solar) | Weather | Copyright-free, attribution "© DWD" | ~500 stations, hourly, 1950s-today | Direct HTTPS, no auth | 5 |
| 2 | energy-charts public_power (wind+solar actual generation) | Energy | CC BY 4.0 (in every payload) | 2015-today, 15-min, DE-LU | GET, no key | 5 |
| 3 | PEGELONLINE river gauges (Rhine/Danube) | Hydrology | DL-DE→Zero-2.0 | 787 gauges, 15-min, live (31-day API window) | Free REST | 5 |
| 4 | EIA-930 hourly grid demand (US) | Energy demand | Public domain | 2015-today, ~65 regions, live | Free API key | 5 |
| 5 | SMARD intraday continuous (15-min ID1/ID3) | Energy | CC BY 4.0 | 15-min products 2021→today | GET, no key | 4.5 |
| 6 | Building Data Genome 2 | Buildings | CC BY-SA 4.0 | 3,053 hourly meters, 2016-17 | Kaggle | 4.5 |
| 7 | BASt motorway traffic counts | Transport | Unnamed on page (verify govdata record) | ~2,126 stations, hourly, 2003-2024 | Direct zips | 3.5 |
| 8 | UBA air quality (PM10/NO2/O3) | Environment | DL-DE→BY-2.0 | 493 stations, hourly, ~2016→ | Free REST | 4 |

## Rejected (verified)

ASHRAE GEPIII (competition license, not open); M5/Rossmann/GEFCom (unclear terms,
no unique event layer); OpenSky flights (free credit quota makes multi-year
extraction infeasible); TfL bikes (terms not confirmed as OGL); NYC TLC (no named
license, well-worn); GBFS (no free history archive); German PT ridership (only
GTFS, no open hourly ridership); ERA5 (CDS queues); Open Power System Data (host
dead); grid frequency (license unclear for redistribution).

## Top 3 in detail

### 1. DWD hourly weather (proposed experiment 03)
- Target: hourly 2m temperature + wind gusts, ~50 German stations, 24-72h ahead.
- Events (frozen on train split): heat hours (>30C), frost (<0C), gusts (>12.5 m/s).
- Business sim: day-ahead energy position priced on heating-degree-days per zone.
- Leakage: clean (observations only); watch station relocations and -999 codes.
- Gotchas: stitch historical + rolling ~150-day recent files per station.

### 2. energy-charts public_power (proposed experiment 04)
- Target: wind+solar generation (or residual load), 15-min, day-ahead.
- Events: forecast-error spikes > P90 (train), solar flat-tops as curtailment proxy.
- Business sim: forecast-driven 4 MWh battery day-ahead bidding, settling forecast
  error at intraday prices - directly comparable to the existing 40.2 EUR/day result.
- Leakage: energy-charts revises recent 15-min values - snapshot before scoring.
- Gotchas: pre-2019 values partly interpolated; zone change DE-AT-LU -> DE-LU 2018.

### 3. PEGELONLINE (future experiment 05 - start collector now)
- Target: Rhine/Danube water levels, 24h ahead.
- Events: official Hochwasserstufen I-IV; KAUB navigation depth 150 cm.
- Business sim: barge load planning - each 10 cm of depth = tonnage per barge.
- Leakage: clean (telemetry); the catch is the 31-day API window: start collecting
  now, optionally backfill context from GRDC.

## Recommended sequence

1. Experiment 03 = DWD weather (safest: frictionless license, 500 stations x 40y,
   distinct domain, strong threshold story).
2. Experiment 04 = energy-charts renewables (ties into the existing price sim).
3. Start the PEGELONLINE collector immediately (zero cost, builds the history a
   future experiment needs).
4. Alternates: EIA-930 (US demand, live leaderboard potential), BDG2 (many
   short-series axis), SMARD intraday 15-min (strongest EUR story, but blocked on
   current filter-ID discovery and a reported 2026 data outage - do second).
