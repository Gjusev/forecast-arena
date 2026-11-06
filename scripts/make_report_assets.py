"""Compute all report assets from stored predictions — the single source of numbers.

Outputs experiments/<exp>/results/report_assets_{tier}/:
  summary_primary.md       headline tables (markdown)
  per_station.md           station-level error table
  dm_tests.md              Diebold-Mariano significance table
  events.md                disruption / negative / spike detection
  scheduling.md + .json    electricity business simulation
  provenance.json          run manifest + thresholds for citation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from forecast_arena.evaluation.analysis import (  # noqa: E402
    dm_vs_baseline,
    event_detection_metrics,
    per_series_metrics,
)
from forecast_arena.evaluation.runner import summarize  # noqa: E402
from forecast_arena.evaluation.simulation import run_simulation  # noqa: E402
from forecast_arena.visualization.charts import MODEL_LABEL  # noqa: E402


def md_table(df: pl.DataFrame) -> str:
    pdf = df.to_pandas()
    if pdf.empty:
        return "_(no data)_"
    return pdf.to_markdown(index=False)


def label(m: str) -> str:
    return MODEL_LABEL.get(m, m)


def export(exp_dir: Path, tier: str, experiment: str, eval_horizons: list[int]) -> Path:
    out = exp_dir / f"report_assets_{tier}"
    out.mkdir(parents=True, exist_ok=True)
    preds = pl.read_parquet(exp_dir / "predictions.parquet").filter(pl.col("tier") == tier)
    thresholds = {}
    thr_path = exp_dir / f"metrics_{tier}.json"
    if thr_path.exists():
        thresholds = json.loads(thr_path.read_text()).get("thresholds", {})

    # headline
    summary = summarize(preds, eval_horizons, baseline_model="seasonal_naive_24h")
    primary = summary.filter(
        pl.col("target").is_in(["avg_delay_min", "day_ahead_price"])
    ).with_columns(pl.col("model").map_elements(label, return_dtype=pl.String))
    (out / "summary_primary.md").write_text(
        "# Headline metrics\n\n"
        + md_table(
            primary.select(
                ["target", "model", "h", "n", "mae", "rmse", "skill_vs_baseline_pct", "coverage_80"]
            )
        )
    )

    # per station (delays) / per hour (electricity)
    ps = per_series_metrics(preds, eval_horizons)
    ps = ps.with_columns(pl.col("model").map_elements(label, return_dtype=pl.String))
    (out / "per_station.md").write_text(
        "# Per-series errors\n\n" + md_table(ps.filter(pl.col("h") == eval_horizons[0]))
    )

    # DM tests
    prefix = "avg_delay_min" if experiment == "train-delays" else "day_ahead_price"
    dm = dm_vs_baseline(preds, eval_horizons, baseline="seasonal_naive_24h", target_prefix=prefix)
    dm = dm.with_columns(pl.col("model").map_elements(label, return_dtype=pl.String))
    (out / "dm_tests.md").write_text(
        "# Diebold-Mariano vs seasonal naive (|error| loss)\n\n"
        "Negative statistic = fewer losses than the baseline. p-value from a HAC "
        "normal approximation; treat families of tests with a multiple-testing "
        "caveat (28 model-horizon tests here).\n\n" + md_table(dm)
    )

    # events
    ev = event_detection_metrics(preds, thresholds, eval_horizons)
    ev = ev.with_columns(pl.col("model").map_elements(label, return_dtype=pl.String))
    (out / "events.md").write_text("# Event detection\n\n" + md_table(ev))

    # scheduling (electricity only)
    if experiment == "electricity":
        best = summary.group_by("model").agg(pl.col("mae").mean()).sort("mae")["model"][0]
        sim = run_simulation(preds.filter(pl.col("model") == best), best)
        (out / "scheduling.md").write_text(
            f"# Scheduling simulation (best model: {label(best)})\n\n"
            "4 MWh flexible load placed in the predicted-cheapest 4 hours of each "
            "delivery day; realized cost at actual prices; wholesale only.\n\n"
            + md_table(
                sim.select(
                    [
                        "origin_ts",
                        "fixed_midday_cost",
                        "model_cost",
                        "oracle_cost",
                        "savings_vs_fixed_eur",
                        "regret_vs_oracle_eur",
                    ]
                ).head(40)
            )
            + "\n\n## Aggregate\n\n"
            + md_table(
                sim.select(
                    pl.col("fixed_midday_cost").mean().alias("fixed_midday_eur_day"),
                    pl.col("model_cost").mean().alias("model_eur_day"),
                    pl.col("oracle_cost").mean().alias("oracle_eur_day"),
                    pl.col("savings_vs_fixed_eur").mean().alias("saving_eur_day"),
                    pl.col("regret_vs_oracle_eur").mean().alias("regret_eur_day"),
                )
            )
        )
        (out / "scheduling.json").write_text(
            json.dumps(
                {
                    "best_model": best,
                    "n_days": sim.height,
                    **sim.select(
                        pl.col("fixed_midday_cost").mean(),
                        pl.col("model_cost").mean(),
                        pl.col("oracle_cost").mean(),
                        pl.col("savings_vs_fixed_eur").mean(),
                        pl.col("regret_vs_oracle_eur").mean(),
                    ).to_dicts()[0],
                },
                indent=2,
            )
        )

    manifest = {}
    mp = exp_dir / f"manifest_{tier}.json"
    if mp.exists():
        manifest = json.loads(mp.read_text())
    (out / "provenance.json").write_text(
        json.dumps({"tier": tier, "thresholds": thresholds, "manifest": manifest}, indent=2)
    )
    print("assets ->", out)
    return out


if __name__ == "__main__":
    tier = sys.argv[1] if len(sys.argv) > 1 else "full"
    export(Path("experiments/01-train-delays/results"), tier, "train-delays", [1, 3, 6, 24])
    export(
        Path("experiments/02-electricity-prices/results"), tier, "electricity", list(range(1, 25))
    )
