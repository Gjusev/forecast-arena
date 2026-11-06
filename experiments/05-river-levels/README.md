# Experiment 05 — German river levels (PEGELONLINE)

**Status:** collecting. The PEGELONLINE REST API (WSV, the federal waterways
service) only serves a ~31-day history window per gauge, so we are accumulating
history locally now — experiment design starts once enough history exists.

## What will live here

24h-ahead water-level forecasting on Rhine/Danube gauges (target: water level
cm at 15-min cadence), with navigation-focused events and sims: official
Hochwasserstufen I-IV flood levels, KAUB gauge as the Rhine navigation choke
point (150 cm fairway), and a barge-load business sim — each 10 cm of extra
depth is tonnage per barge.

## Run the collector

```bash
uv run python scripts/collect_pegelonline.py                # all ~738 gauges with W
uv run python scripts/collect_pegelonline.py --stations KAUB,CELLE
uv run python scripts/collect_pegelonline.py --max-stations 25   # quick test
```

Appends/dedupes into `data/raw/hydro/pegel_levels.parquet`
(`timestamp` tz-aware Europe/Berlin, `value` cm, `zone` station shortname,
`target` "water_level"). `data/` is gitignored — the script is the reproducible
entry point; run it daily to grow the dataset.

## Dataset facts

- Source: [PEGELONLINE REST API v2](https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations)
- License: DL-DE→Zero-2.0 (free, no attribution required)
- ~738 of 787 gauges report water level `W`; 15-min cadence, ~31-day rolling window
- Access and license verified live 2026-11-06; see
  [docs/dataset-research.md](../../docs/dataset-research.md) for the full
  candidate assessment
