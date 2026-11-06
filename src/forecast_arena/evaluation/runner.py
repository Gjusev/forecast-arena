"""Benchmark executor: rolling origins x models x series -> predictions + metrics.

Resumable: existing prediction rows for (experiment, tier, model, origin) are
skipped on re-run. Timing is wall-clock per forecast call; memory is sampled
process RSS (approximate, stated as such in the manifest).
"""

from __future__ import annotations

import json
import logging
import platform
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import polars as pl

from forecast_arena.evaluation import metrics as M
from forecast_arena.evaluation.protocol import PanelSpec
from forecast_arena.models.base import Forecaster, KnownFuture

log = logging.getLogger(__name__)

PRED_COLS = [
    "experiment",
    "tier",
    "model",
    "series_id",
    "origin_ts",
    "h",
    "y_true",
    "y_pred",
    "q05",
    "q10",
    "q25",
    "q75",
    "q90",
    "q95",
]


@dataclass
class RunManifest:
    experiment: str
    tier: str
    n_series: int
    horizon: int
    origins: list[int]
    models: list[str]
    python: str
    platform: str
    started: str
    finished: str | None = None
    wall_seconds: float | None = None
    per_model_seconds: dict[str, float] | None = None


def _peak_rss_mb() -> float:
    try:
        import psutil

        return psutil.Process().memory_info().rss / 1e6
    except Exception:
        return float("nan")


def impute_hour_of_week(hist: np.ndarray) -> np.ndarray:
    """Fill NaN slots with the series' own hour-of-week mean (past data only).

    No-arrival hours have null avg delay; 'no trains' is not 'zero delay'.
    Imputation uses only the history passed in (which ends at the origin), so
    every model sees identical, leakage-free inputs. Applies to all models
    alike, including those that could handle NaN natively.
    """
    h = np.asarray(hist, dtype=float).copy()
    nan = ~np.isfinite(h)
    if not nan.any():
        return h
    how = np.arange(len(h)) % 168
    finite = ~nan
    sums = np.bincount(how[finite], weights=h[finite], minlength=168)
    counts = np.bincount(how[finite], minlength=168).astype(float)
    means = np.divide(sums, counts, out=np.full(168, np.nan), where=counts > 0)
    fallback = float(np.mean(h[finite])) if finite.any() else 0.0
    means = np.where(np.isfinite(means), means, fallback)
    h[nan] = means[how[nan]]
    return h


def run_benchmark(
    experiment: str,
    tier: str,
    spec: PanelSpec,
    models: list[Forecaster],
    out_dir: Path,
    origin_datetimes: dict[int, str] | None = None,
    grid_how: np.ndarray | None = None,
    max_context: int = 512,
) -> pl.DataFrame:
    """Execute all (model, origin, series) forecasts; append to predictions.parquet.

    grid_how: DST-correct hour-of-week per grid slot; passed to models that
    need calendar features and to every forecast as KnownFuture.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "predictions.parquet"
    done: set[tuple[str, int]] = set()
    if pred_path.exists():
        old = pl.read_parquet(pred_path)
        done = {
            (m, o)
            for m, o in zip(old["model"].to_list(), old["origin_ts"].to_list(), strict=False)
            if old["tier"][0] == tier
        }
        # simpler & safe: recompute done set with filter
        old_f = old.filter(pl.col("tier") == tier)
        done = set(zip(old_f["model"].to_list(), old_f["origin_ts"].to_list(), strict=False))

    per_model_seconds: dict[str, float] = {}
    rows: list[dict] = []
    origins = spec.origins()
    log.info(
        "[%s/%s] %d origins, %d models, %d series",
        experiment,
        tier,
        len(origins),
        len(models),
        len(spec.series),
    )

    if grid_how is not None:
        for m in models:
            if hasattr(m, "set_calendar"):
                m.set_calendar(grid_how)
    last_prepare: dict[str, int] = {}

    for model in models:
        t_model = 0.0
        for origin in origins:
            # resumability: stored rows carry the origin's timestamp label, so
            # compare against that label (origins themselves are grid indices)
            o_label = (origin_datetimes or {}).get(origin, str(origin))
            if (model.name, o_label) in done:
                continue
            histories = {
                sid: impute_hour_of_week(v[:origin])[-max_context:]
                for sid, v in spec.series.items()
            }
            full_histories = {
                sid: impute_hour_of_week(v[:origin]) for sid, v in spec.series.items()
            }
            t0 = time.perf_counter()
            refit_every = int(getattr(model, "refit_every", 1))
            due = model.name not in last_prepare or (
                origin - last_prepare[model.name] >= refit_every * spec.origin_step
            )
            if due:
                model.prepare(full_histories, origin)
                last_prepare[model.name] = origin
            t_prep = time.perf_counter() - t0
            t_model += t_prep
            o_ts = o_label
            for sid, h in histories.items():
                known = None
                if grid_how is not None and origin + spec.horizon <= len(grid_how):
                    known = KnownFuture(
                        columns=["hour_of_week"],
                        values=grid_how[origin : origin + spec.horizon].reshape(-1, 1),
                    )
                t1 = time.perf_counter()
                res = model.forecast(h, spec.horizon, known_future=known, series_id=sid)
                t_model += time.perf_counter() - t1
                y = spec.series[sid][origin : origin + spec.horizon]
                base = {
                    "experiment": experiment,
                    "tier": tier,
                    "model": model.name,
                    "series_id": sid,
                    "origin_ts": o_ts,
                    "y_true": y.astype(float).tolist(),
                    "y_pred": res.point.astype(float).tolist(),
                }
                if res.quantiles is not None and res.quantile_levels is not None:
                    for qname in ["q05", "q10", "q25", "q75", "q90", "q95"]:
                        lvl = float(qname[1:]) / 100
                        i = int(np.argmin(np.abs(res.quantile_levels - lvl)))
                        base[qname] = res.quantiles[:, i].astype(float).tolist()
                else:
                    for qname in ["q05", "q10", "q25", "q75", "q90", "q95"]:
                        base[qname] = [None] * spec.horizon
                rows.append(base)
            if len(rows) >= 200:
                _append_rows(pred_path, rows, spec)
                rows = []
        per_model_seconds[model.name] = t_model

    if rows:
        _append_rows(pred_path, rows, spec)
    manifest = RunManifest(
        experiment=experiment,
        tier=tier,
        n_series=len(spec.series),
        horizon=spec.horizon,
        origins=origins,
        models=[m.name for m in models],
        python=platform.python_version(),
        platform=platform.platform(),
        started=time.strftime("%Y-%m-%dT%H:%M:%S"),
        finished=time.strftime("%Y-%m-%dT%H:%M:%S"),
        wall_seconds=None,
        per_model_seconds=per_model_seconds,
    )
    (out_dir / f"manifest_{tier}.json").write_text(json.dumps(asdict(manifest), indent=2))
    return pl.read_parquet(pred_path).filter(pl.col("tier") == tier)


def _append_rows(path: Path, rows: list[dict], spec: PanelSpec) -> None:
    # long format: one row per (record, step)
    data = {c: [] for c in PRED_COLS}
    for r in rows:
        for i in range(spec.horizon):
            data["experiment"].append(r["experiment"])
            data["tier"].append(r["tier"])
            data["model"].append(r["model"])
            data["series_id"].append(r["series_id"])
            data["origin_ts"].append(r["origin_ts"])
            data["h"].append(i + 1)
            data["y_true"].append(r["y_true"][i])
            data["y_pred"].append(r["y_pred"][i])
            for q in ["q05", "q10", "q25", "q75", "q90", "q95"]:
                v = r[q][i] if r[q] else None
                data[q].append(v)
    df = pl.DataFrame(data)
    if path.exists():
        old = pl.read_parquet(path)
        df = pl.concat([old, df], how="diagonal")
    df.write_parquet(path)


def summarize(
    preds: pl.DataFrame,
    eval_horizons: list[int],
    baseline_model: str,
    event_thresholds: dict[str, float] | None = None,
) -> pl.DataFrame:
    """Metrics per (model, target, h).

    Series of one target share units and pool together; different targets
    never mix.
    """
    pdf = preds.to_pandas()
    pdf["target"] = pdf.series_id.str.split("/").str[0]
    out = []
    baseline = pdf[pdf.model == baseline_model]
    for (model, target, h), g in pdf.groupby(["model", "target", "h"]):
        if h not in eval_horizons:
            continue
        y = g["y_true"].to_numpy(float)
        p = g["y_pred"].to_numpy(float)
        bl = baseline[(baseline.h == h) & (baseline.target == target)]
        pairs = list(zip(bl.series_id, bl.origin_ts, strict=True))
        bl_by = dict(zip(pairs, bl.y_pred, strict=True))
        keys = list(zip(g.series_id, g.origin_ts, strict=False))
        if all(k in bl_by for k in keys) and len(bl_by) > 0:
            bl_pred = np.array([bl_by[k] for k in keys])
            skill = float(100 * (1 - M.mae(y, p) / M.mae(y, bl_pred)))
        else:
            skill = float("nan")
        row = {
            "model": model,
            "target": target,
            "h": int(h),
            "n": len(g),
            "mae": M.mae(y, p),
            "rmse": M.rmse(y, p),
            "smape": M.smape(y, p),
            "skill_vs_baseline_pct": skill,
        }
        if {"q05", "q95"} <= set(g.columns):
            lo, hi = g["q05"].to_numpy(float), g["q95"].to_numpy(float)
            row["coverage_90"] = M.interval_coverage(y, lo, hi)
        if {"q10", "q90"} <= set(g.columns):
            lo, hi = g["q10"].to_numpy(float), g["q90"].to_numpy(float)
            row["coverage_80"] = M.interval_coverage(y, lo, hi)
        if event_thresholds:
            thr = event_thresholds.get(g.series_id.iloc[0], float("nan"))
            if np.isfinite(thr):
                det = M.event_detection(y, p, thr)
                row.update({f"evt_{k}": v for k, v in det.items()})
        out.append(row)
    return pl.DataFrame(out).sort(["target", "h", "mae"])
