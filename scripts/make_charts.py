"""Generate publication charts from stored full-tier results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from forecast_arena.evaluation.analysis import event_detection_metrics  # noqa: E402
from forecast_arena.evaluation.runner import summarize  # noqa: E402
from forecast_arena.visualization import charts as C  # noqa: E402

ASSETS = Path("assets/charts")


def delays():
    exp = Path("experiments/01-train-delays/results")
    preds = pl.read_parquet(exp / "predictions.parquet").filter(pl.col("tier") == "full")
    metrics = pl.read_parquet(exp / "metrics_full.parquet")
    man = json.loads((exp / "manifest_full.json").read_text())
    secs = man.get("per_model_seconds") or {}

    C.fig_model_accuracy(
        metrics, "avg_delay_min", 1, ASSETS,
        "Train delay forecasting — average arrival delay, 1 hour ahead\n"
        "5 German hub stations · 110 rolling origins · 2026",
    )
    C.fig_model_accuracy(
        metrics, "n_delayed_gt5", 1, ASSETS,
        "Disruption forecasting — delayed arrivals per hour, 1 hour ahead\n"
        "5 German hub stations · 110 rolling origins · 2026",
    )
    C.fig_accuracy_runtime(
        metrics, secs, "avg_delay_min", 1, ASSETS,
        "Accuracy vs compute — train delays, 1 hour ahead",
    )
    # actual vs predicted: pick a high-disruption Frankfurt origin
    series = "avg_delay_min/Frankfurt(Main)Hbf"
    fk = preds.filter(
        (pl.col("series_id") == series)
        & (pl.col("model") == "seasonal_naive_24h")
        & (pl.col("h") == 1)
    )
    worst = fk.sort("y_true", descending=True)["origin_ts"][0]
    C.fig_actual_vs_predicted(
        preds, series, worst, ASSETS,
        f"Forecasting a disruption day — Frankfurt (Main) Hbf, origin {worst[:10]}",
    )
    # detection chart on the secondary target
    thr = json.loads((exp / "metrics_full.json").read_text()).get("thresholds", {})
    ev = event_detection_metrics(
        preds.filter(pl.col("series_id").str.starts_with("n_delayed_gt5")), thr, [1, 6]
    )
    ev = ev.group_by("model").agg(
        pl.col("evt_precision").mean(), pl.col("evt_recall").mean()
    )
    C.fig_detection(ev, "evt_", ASSETS, "Disruption-hour detection (per-station P90 threshold)")


def electricity():
    exp = Path("experiments/02-electricity-prices/results")
    preds = pl.read_parquet(exp / "predictions.parquet").filter(pl.col("tier") == "full")
    metrics = pl.read_parquet(exp / "metrics_full.parquet")
    man = json.loads((exp / "manifest_full.json").read_text())
    secs = man.get("per_model_seconds") or {}

    pooled = summarize(preds, [1], baseline_model="seasonal_naive_24h")
    # single pooled row per model: average over delivery hours
    pooled = metrics.group_by("model").agg(
        pl.col("mae").mean(), pl.col("rmse").mean(),
        pl.col("skill_vs_baseline_pct").mean(), pl.col("coverage_80").mean(),
        pl.lit("day_ahead_price").alias("target"), pl.lit(1).alias("h"),
        pl.len().alias("n"),
    )
    C.fig_model_accuracy(
        pooled, "day_ahead_price", 1, ASSETS,
        "Day-ahead price forecasting — German bidding zone\n"
        "MAE pooled over all 24 delivery hours · daily pre-auction origins",
    )
    C.fig_accuracy_runtime(
        pooled, secs, "day_ahead_price", 1, ASSETS,
        "Accuracy vs compute — day-ahead prices",
    )
    series = "day_ahead_price/DE-LU"
    # find a day with negative prices
    neg = preds.filter((pl.col("model") == "seasonal_naive_24h") & (pl.col("y_true") < 0))
    day = neg["origin_ts"].unique().sort()[-1] if neg.height else None
    if day:
        C.fig_actual_vs_predicted(
            preds, series, day, ASSETS,
            f"Forecasting a negative-price day — DE-LU day-ahead, delivery {day[:10]}",
        )
    # scheduling
    from forecast_arena.evaluation.simulation import run_simulation

    best = pooled.sort("mae")["model"][0]
    sim = run_simulation(preds.filter(pl.col("model") == best), best)
    C.fig_scheduling(sim, ASSETS, f"Flexible load scheduling by price forecast ({best})")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "delays"):
        delays()
    if which in ("all", "electricity"):
        electricity()
    print("charts ->", ASSETS)
