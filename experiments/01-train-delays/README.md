# Experiment 01 — Deutsche Bahn train delays

**Working title:** *Can Mistral's 209M model predict German train delays?*

## Research question

Can zero-shot time series foundation models predict station-level disruption
hours ahead — and beat the seasonal-naive bar and gradient-boosted trees doing it?

## Dataset

[piebro/deutsche-bahn-data](https://huggingface.co/datasets/piebro/deutsche-bahn-data)
(CC-BY-4.0) — aggregated Deutsche Bahn timetable data, *finalized* per-stop
records with precomputed `delay_in_min` and `arrival_is_canceled`:

- Coverage: 2024-07 → 2026-10 (28 months), ~5.7M arrivals across the 5 stations
- Stations (multi-EVA unions, resolved from the data): Frankfurt (Main) Hbf,
  Köln Hbf, München Hbf, Berlin Hauptbahnhof, Hamburg Hbf
- Timestamps are Berlin wall clock (DST transitions verified empirically)

## Protocol — completed-hour (ADR-0001)

Forecast origin = end of the last fully completed hour. Models see only
hourly aggregates of completed hours + calendar. Targets = the next hours'
aggregates at h = 1, 3, 6, 24 steps. No train-level future information exists
in any input; en-route features are documented as a data-limited stretch goal
(snapshots exist but only every ~6 hours).

- **Primary target:** average arrival delay (minutes)
- **Secondary target:** delayed-arrival count (>5 min) per hour — drives
  disruption detection
- Missing avg-delay hours (no arrivals) are imputed with the series' own
  hour-of-week mean from data ≤ origin, identically for every model
- Origins: ~weekly cadence with a 167-hour phase rotation, so short horizons
  are evaluated across all hours of the week (not just one wall-clock hour)
- Disruption-hour threshold: per-station P90 of the delayed count, **frozen on
  training data only**

## Models

See the [root README](../../README.md) — all 8 compete under identical inputs.

## Results

Located in `results/` (`metrics_{tier}.parquet`, `predictions.parquet`,
`report_assets_{tier}/`). Verified headline numbers live in the
[technical report](../../reports/01-train-delays.md) — never edited by hand.

## Reproduce

```bash
uv sync --group dev --extra ml --extra foundation
uv run arena build-data 01
uv run --extra ml --extra foundation arena run 01 --tier smoke   # minutes
uv run --extra ml --extra foundation arena run 01 --tier pilot   # ~2 min
uv run --extra ml --extra foundation arena run 01 --tier full
uv run python scripts/make_report_assets.py full
```

## Limitations

- Finalized records → this is an *operational-planning* forecast, not a
  dispatch-system forecast (they see en-route trains; we cannot).
- Five major hubs only; regional stations will behave differently.
- Delay = change-time − planned-time where a change exists, else 0 (on time);
  the dataset encodes punctuality as absence of change messages.
