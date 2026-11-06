"""Post-benchmark analysis: per-station errors, DM tests, event detection.

Consumes the long-format predictions parquet produced by the runner.
"""

from __future__ import annotations

import numpy as np
import polars as pl

from forecast_arena.evaluation import metrics as M


def _to_np(g: pl.DataFrame, col: str) -> np.ndarray:
    return g[col].to_numpy().astype(float)


def per_series_metrics(preds: pl.DataFrame, eval_horizons: list[int]) -> pl.DataFrame:
    """MAE/RMSE per (model, series_id, h) for detailed station-level tables."""
    pdf = preds.to_pandas()
    out = []
    for (model, sid, h), g in pdf.groupby(["model", "series_id", "h"]):
        if h not in eval_horizons:
            continue
        y, p = g["y_true"].to_numpy(float), g["y_pred"].to_numpy(float)
        out.append(
            {
                "model": model,
                "series_id": sid,
                "h": int(h),
                "n": len(g),
                "mae": M.mae(y, p),
                "rmse": M.rmse(y, p),
            }
        )
    return pl.DataFrame(out).sort(["series_id", "h", "mae"])


def dm_vs_baseline(
    preds: pl.DataFrame,
    eval_horizons: list[int],
    baseline: str = "seasonal_naive_24h",
    target_prefix: str = "",
) -> pl.DataFrame:
    """Diebold-Mariano: each model vs the baseline, per horizon.

    Negative statistic = model loses LESS than baseline (better).
    """
    pdf = preds.to_pandas()
    if target_prefix:
        pdf = pdf[pdf.series_id.str.startswith(target_prefix)]
    out = []
    for h in eval_horizons:
        bl = pdf[(pdf.model == baseline) & (pdf.h == h)]
        if bl.empty:
            continue
        bl_map = {(s, o): p for s, o, p in zip(bl.series_id, bl.origin_ts, bl.y_pred, strict=True)}
        for model in pdf.model.unique():
            g = pdf[(pdf.model == model) & (pdf.h == h)]
            if g.empty or model == baseline:
                continue
            keys = [(s, o) for s, o in zip(g.series_id, g.origin_ts, strict=True)]
            if not all(k in bl_map for k in keys):
                continue
            y = g.y_true.to_numpy(float)
            e_model = y - g.y_pred.to_numpy(float)
            e_base = y - np.array([bl_map[k] for k in keys])
            stat, p = M.diebold_mariano(e_model, e_base, loss="ae", h=max(1, h))
            out.append(
                {
                    "model": model,
                    "h": int(h),
                    "dm_stat": stat,
                    "p_value": p,
                    "better_than_baseline": bool(stat < 0),
                }
            )
    return pl.DataFrame(out).sort(["h", "p_value"])


def event_detection_metrics(
    preds: pl.DataFrame,
    thresholds: dict[str, float],
    eval_horizons: list[int],
) -> pl.DataFrame:
    """Disruption/negative/spike detection per model.

    For negative-price events the detection uses (y < 0) vs (pred < 0); for
    threshold events (y >= thr) vs (pred >= thr).
    """
    pdf = preds.to_pandas()
    out = []
    for (model, sid), g in pdf.groupby(["model", "series_id"]):
        target = sid.split("/")[0]
        for h in eval_horizons:
            gh = g[g.h == h]
            if gh.empty:
                continue
            y = gh.y_true.to_numpy(float)
            p = gh.y_pred.to_numpy(float)
            row = {"model": model, "series_id": sid, "h": int(h)}
            if target == "day_ahead_price" or "day_ahead" in target:
                neg = M.event_detection(-y, -p, threshold=0.0)
                row.update({f"neg_{k}": v for k, v in neg.items()})
            thr = thresholds.get(sid, float("nan"))
            if np.isfinite(thr):
                det = M.event_detection(y, p, thr)
                row.update({f"evt_{k}": v for k, v in det.items()})
            out.append(row)
    return pl.DataFrame(out)
