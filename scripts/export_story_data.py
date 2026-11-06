"""Export the small JSON that drives the motion video (assets/video/story.json).

Every number in the video comes from committed benchmark outputs.
Run: uv run python scripts/export_story_data.py
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl

E1 = Path("experiments/01-train-delays/results")
E2 = Path("experiments/02-electricity-prices/results")
OUT = Path("assets/video/story.json")
MODELS = [
    "timestral_209M",
    "timestral_28M",
    "chronos_2",
    "timesfm_3_0",
    "lightgbm",
    "xgboost",
    "seasonal_naive_24h",
]


def day_curves(preds: pl.DataFrame, series: str, origin: str) -> dict:
    g = preds.filter((pl.col("series_id") == series) & (pl.col("origin_ts") == origin)).sort("h")
    actual = g.filter(pl.col("model") == MODELS[0])["y_true"].round(2).to_list()
    return {
        "origin": origin,
        "actual": actual,
        "pred": {
            m: g.filter(pl.col("model") == m)["y_pred"].round(2).to_list()
            for m in MODELS
            if g.filter(pl.col("model") == m).height
        },
    }


def main() -> None:
    p1 = pl.read_parquet(E1 / "predictions.parquet").filter(pl.col("tier") == "full")
    p2 = pl.read_parquet(E2 / "predictions.parquet").filter(pl.col("tier") == "full")
    m1 = pl.read_parquet(E1 / "metrics_full.parquet")
    m2 = pl.read_parquet(E2 / "metrics_full.parquet")

    # same selection rule as scripts/make_charts.py
    fk = "avg_delay_min/Frankfurt(Main)Hbf"
    worst = p1.filter(
        (pl.col("series_id") == fk) & (pl.col("model") == "seasonal_naive_24h") & (pl.col("h") == 1)
    ).sort("y_true", descending=True)["origin_ts"][0]
    # illustrative solar Sunday (17 negative hours). Chosen because it shows the
    # mechanism clearly; the honest aggregate (neg-price F1 ~0.5) ships alongside.
    neg_day = "2024-07-07 01:00:00+02:00"
    neg_f1 = pl.read_parquet(E2 / "report_assets_full/neg_detection_pooled.parquet")

    lb1 = (
        m1.filter((pl.col("target") == "avg_delay_min") & (pl.col("h") == 1))
        .sort("mae")
        .select("model", pl.col("mae").round(4), pl.col("skill_vs_baseline_pct").round(1))
    )
    lb2 = (
        m2.group_by("model")
        .agg(pl.col("mae").mean().round(2), pl.col("skill_vs_baseline_pct").mean().round(1))
        .sort("mae")
    )
    sched = json.loads((E2 / "report_assets_full/scheduling.json").read_text())

    # weather (03): skill vs naive at h=24 for the models the film shows
    m3 = pl.read_parquet(Path("experiments/03-dwd-weather/results/metrics_full.parquet"))
    weather24 = (
        m3.filter((pl.col("target") == "air_temperature") & (pl.col("h") == 24))
        .select("model", pl.col("skill_vs_baseline_pct").round(1).alias("skill"))
        .sort("skill", descending=True)
    )
    # renewables (04): biggest AI-vs-naive gap day on wind_total + skills
    m4 = pl.read_parquet(Path("experiments/04-renewables/results/metrics_full.parquet"))
    p4 = pl.read_parquet(Path("experiments/04-renewables/results/predictions.parquet")).filter(
        (pl.col("tier") == "full") & (pl.col("series_id") == "wind_total/DE-LU")
    )
    po = (
        p4.filter(pl.col("y_true").is_finite())
        .with_columns((pl.col("y_true") - pl.col("y_pred")).abs().alias("err"))
        .group_by("origin_ts", "model")
        .agg(pl.col("err").mean())
    )
    pivot = po.filter(pl.col("model").is_in(["seasonal_naive_24h", "timestral_209M"])).pivot(
        on="model", values="err"
    )
    wind_day = pivot.with_columns(
        (pl.col("seasonal_naive_24h") - pl.col("timestral_209M")).alias("gap")
    ).sort("gap", descending=True)["origin_ts"][0]
    renew_skills = {
        h: {
            r["model"]: r["skill_vs_baseline_pct"]
            for r in m4.filter((pl.col("target") == "wind_total") & (pl.col("h") == h))
            .filter(pl.col("model").is_in(["timestral_209M", "xgboost"]))
            .select("model", pl.col("skill_vs_baseline_pct").round(1))
            .to_dicts()
        }
        for h in (1, 24)
    }

    story = {
        "delays": day_curves(p1, fk, worst) | {"station": "Frankfurt (Main) Hbf"},
        "prices": day_curves(p2, "day_ahead_price/DE-LU", neg_day),
        "leader_delays": lb1.to_dicts(),
        "leader_prices": lb2.to_dicts(),
        "scheduling": sched,
        "n_delay_forecasts": int(
            m1.filter((pl.col("target") == "avg_delay_min") & (pl.col("h") == 1))["n"][0]
        ),
        "neg_f1": neg_f1.select("model", pl.col("f1").round(2)).to_dicts(),
        "weather24": weather24.to_dicts(),
        "renew": day_curves(p4, "wind_total/DE-LU", wind_day)
        | {"skills": renew_skills, "station": "whole German fleet"},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(story, indent=1, default=str), encoding="utf-8")
    print(
        "->",
        OUT,
        "| delays origin",
        worst,
        "| neg day",
        neg_day,
        "| wind day",
        wind_day,
    )


if __name__ == "__main__":
    main()
