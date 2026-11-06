"""Live forecast: publish tomorrow's day-ahead price forecasts before reality.

Protocol (ADR-0002 completed-hours semantics):
 1. refresh the SMARD day-ahead cache,
 2. forecast delivery day D using ONLY prices through D-1 23:00,
 3. the git commit is the tamper-evident publication,
 4. once D's actual prices are published, score the committed forecast.

Outputs under live/: predictions.parquet (tier=live), scores.json, pending.json.
Run: uv run --no-sync python scripts/live_forecast.py
Flags: --fast (3 models), --live-dir, --delivery-day YYYY-MM-DD (past day
forces a forecast+score in one run).
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl

from forecast_arena.config import load_config
from forecast_arena.data.electricity import build_price_panel
from forecast_arena.data.panels import grid_and_series
from forecast_arena.evaluation.protocol import PanelSpec
from forecast_arena.evaluation.runner import run_benchmark
from forecast_arena.experiment import build_models

log = logging.getLogger("live")
TZ = "Europe/Berlin"
ALL_MODELS = [
    "seasonal_naive_24h",
    "hour_of_week_climatology",
    "lightgbm",
    "xgboost",
    "timestral_28m",
    "timestral_209m",
    "chronos_2",
    "timesfm_3_0",
]
FAST_MODELS = ["seasonal_naive_24h", "lightgbm", "chronos_2"]


def _refresh_prices(cache: Path) -> pl.DataFrame:
    """SMARD prices refreshed, with the target/zone columns the panel needs."""
    df = build_price_panel(cache, refresh=True).select("timestamp", "value")
    df = df.with_columns(pl.col("value").cast(pl.Float64))
    df = df.with_columns(pl.lit("DE-LU").alias("zone"), pl.lit("day_ahead_price").alias("target"))
    return df


def panel_for_delivery(
    df: pl.DataFrame, delivery_day: str, start: str | None
) -> tuple[np.ndarray, dict[str, np.ndarray], str, int]:
    """Series dict ending at delivery day D's 24th hour.

    D's slots keep real values where SMARD has published them, NaN otherwise.
    The forecast information cut is everything strictly before D. Returns
    (grid_how, series, origin_ts_label, n_real); the forecast origin index
    is n_real (first slot of D).
    """
    if start:
        df = df.filter(pl.col("timestamp") >= pl.lit(start).str.to_datetime(time_zone=TZ))
    df = df.filter(pl.col("timestamp").dt.date() < pl.lit(delivery_day).str.to_date())
    grid_real = df.select("timestamp").unique().sort("timestamp")["timestamp"].to_list()
    n_real = len(grid_real)
    fut = [grid_real[-1] + timedelta(hours=i) for i in range(1, 25)]
    keep = df.select("timestamp", "value", "target", "zone")
    fut_df = pl.DataFrame(
        {
            "timestamp": fut,
            "value": [None] * 24,
            "target": ["day_ahead_price"] * 24,
            "zone": ["DE-LU"] * 24,
        },
        schema=keep.schema,
    )
    df_all = pl.concat([keep, fut_df], how="vertical")
    _, grid_how, series = grid_and_series(df_all, "timestamp", ["target", "zone"], "value")
    if grid_how.shape[0] != n_real + 24:
        raise RuntimeError(f"panel/grid mismatch: {grid_how.shape[0]} vs {n_real}+24")
    return grid_how, series, str(fut[0]), n_real


def score_history(pred_path: Path, real: pl.DataFrame) -> dict:
    """Score every stored live origin whose 24 delivery hours are published."""
    if not pred_path.exists():
        return {"scored": [], "leaderboard": []}
    preds = pl.read_parquet(pred_path).filter(pl.col("tier") == "live")
    pos = {t.timestamp(): i for i, t in enumerate(real["timestamp"].to_list())}
    values = real["value"].to_list()
    scored: list[dict] = []
    board: dict[str, list[float]] = {}
    for origin_s in sorted(preds["origin_ts"].unique().to_list()):
        d0 = datetime.fromisoformat(origin_s)
        actual = []
        for h in range(24):
            i = pos.get((d0 + timedelta(hours=h)).timestamp())
            v = values[i] if i is not None else None
            actual.append(v)
        if any(v is None or v != v for v in actual):
            continue  # delivery day not fully published yet
        y = np.array(actual, dtype=float)
        day: dict = {"origin_ts": origin_s, "models": {}}
        g = preds.filter(pl.col("origin_ts") == origin_s)
        for m in sorted(g["model"].unique().to_list()):
            r = g.filter(pl.col("model") == m).sort("h")
            p = np.array(r["y_pred"].to_list(), dtype=float)
            lo = np.array(r["q10"].to_list(), dtype=float)
            hi = np.array(r["q90"].to_list(), dtype=float)
            entry = {"mae": round(float(np.mean(np.abs(y - p))), 3)}
            if np.isfinite(lo).all() and np.isfinite(hi).all():
                entry["coverage_80"] = round(float(np.mean((y >= lo) & (y <= hi))), 3)
            day["models"][m] = entry
            board.setdefault(m, []).append(entry["mae"])
        scored.append(day)
    leaderboard = sorted(
        (
            {"model": m, "mean_mae": round(float(np.mean(v)), 3), "n": len(v)}
            for m, v in board.items()
        ),
        key=lambda r: r["mean_mae"],
    )
    return {"scored": scored, "leaderboard": leaderboard}


def build_pending(pred_path: Path, scored: dict, published_utc: str) -> dict:
    """Rebuild the JSON view of the newest unscored forecast."""
    preds = pl.read_parquet(pred_path).filter(pl.col("tier") == "live")
    done = {d["origin_ts"] for d in scored["scored"]}
    open_origins = sorted(set(preds["origin_ts"].to_list()) - done)
    if not open_origins:
        return {"status": "none", "note": "no unscored forecast yet"}
    origin_s = open_origins[-1]
    g = preds.filter(pl.col("origin_ts") == origin_s)
    return {
        "status": "pending",
        "origin_ts": origin_s,
        "delivery_day": origin_s[:10],
        "published_utc": published_utc,
        "protocol": "ADR-0002 completed-hours: information cut at delivery day minus 1, 23:00",
        "forecasts": {
            m: {
                "point": r.sort("h")["y_pred"].to_list(),
                "q10": r.sort("h")["q10"].to_list(),
                "q90": r.sort("h")["q90"].to_list(),
            }
            for (m,), r in g.group_by("model")
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="3 fast models only")
    ap.add_argument("--live-dir", default="live")
    ap.add_argument("--delivery-day", default=None, help="force delivery day YYYY-MM-DD")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cfg = load_config(Path("experiments/02-electricity-prices/config.yaml"))
    live_dir = Path(args.live_dir)
    live_dir.mkdir(parents=True, exist_ok=True)
    pred_path = live_dir / "predictions.parquet"

    real = _refresh_prices(Path(cfg["data"]["prices"]))
    latest_date = real["timestamp"].max().date()
    if latest_date < datetime.now(UTC).date() - timedelta(days=2):
        log.warning("SMARD data looks stale (latest %s)", latest_date)

    if args.delivery_day:
        delivery_day = args.delivery_day
    else:
        complete = (
            real.drop_nulls("value")
            .group_by(pl.col("timestamp").dt.date().alias("d"))
            .agg(pl.len().alias("n"))
            .filter(pl.col("n") >= 24)
        )
        delivery_day = str(complete["d"].max() + timedelta(days=1))
    if delivery_day <= str(latest_date):
        log.info("delivery day %s already published - scoring run", delivery_day)

    how, series, origin_label, n_real = panel_for_delivery(
        real, delivery_day, cfg.get("data", {}).get("start")
    )
    origin = n_real
    models = build_models(FAST_MODELS if args.fast else ALL_MODELS)
    log.info("delivery day %s | %d models", delivery_day, len(models))

    ok: list[str] = []
    failed: list[str] = []
    for model in models:
        try:
            run_benchmark(
                "electricity",
                "live",
                PanelSpec(
                    series=series,
                    horizon=24,
                    origin_step=24,
                    min_train=origin,
                    eval_horizons=list(range(1, 25)),
                ),
                [model],
                live_dir,
                origin_datetimes={origin: origin_label},
                grid_how=how,
            )
            ok.append(model.name)
        except Exception as exc:  # noqa: BLE001 - daily cron must survive one bad model
            failed.append(model.name)
            log.error("model %s failed: %s", model.name, exc)

    scored = score_history(pred_path, real)
    published = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    pending = build_pending(pred_path, scored, published)
    pending["models_run"] = ok
    pending["models_failed"] = failed
    (live_dir / "scores.json").write_text(json.dumps(scored, indent=1), encoding="utf-8")
    (live_dir / "pending.json").write_text(json.dumps(pending, indent=1), encoding="utf-8")

    log.info("models ok: %s%s", ok, f" | FAILED: {failed}" if failed else "")
    if scored["leaderboard"]:
        log.info("leaderboard: %s", scored["leaderboard"][:3])
    log.info("pending: %s", {k: pending.get(k) for k in ("status", "delivery_day")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
