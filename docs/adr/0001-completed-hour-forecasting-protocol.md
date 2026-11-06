# ADR 0001: Completed-hour forecasting protocol for train delays

## Status

Accepted (2026-11-06)

## Context

Deutsche Bahn delay datasets typically store *finalized* arrival records: a row's
"actual arrival" is knowable only after the train arrives. A forecasting setup that
feeds such rows into predictions for earlier timestamps leaks the future and inflates
apparent accuracy. Real-time snapshots (what was known *at* prediction time) are
usually not preserved.

## Decision

For the train-delays experiment, all models — foundation, ML, and statistical
baselines alike — operate under the **completed-hour protocol**:

1. Series are hourly aggregates per station (e.g. average arrival delay in minutes
   over trains scheduled to arrive in that hour).
2. The forecast origin is the end of the last fully completed hour. Only aggregates
   of completed hours, plus calendar features, are available as inputs.
3. Targets are the aggregates of future hours at fixed horizons (1h, 3h, 6h, 24h
   ahead of the origin).
4. We frame this as an **operational-planning forecast** (predicting disruption
   levels hours ahead from completed observations) — not individual-train
   prediction. The limitation is stated in every report.

If the dataset is later verified to preserve real-time update fields, en-route
features may be added as a stretch goal without redesigning the protocol.

## Consequences

- No future information can reach any model through features; leakage review
  reduces to checking "input hour < forecast origin".
- Hour-boundary effects (trains arriving late within hour H are counted in H's
  aggregate, completed only at H's end) are accepted as part of the task.
- Weaker than real dispatch systems (which see en-route trains), so results are a
  *lower bound* on operational usefulness — stated, not hidden.
