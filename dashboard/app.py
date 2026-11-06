"""forecast-arena dashboard — cached benchmark results, no live inference.

Run:  uv run --extra dashboard python dashboard/app.py   -> http://7860
Reads only the parquet/JSON artifacts under experiments/*/results.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from forecast_arena.evaluation.simulation import run_simulation
from forecast_arena.visualization.charts import (
    ACTUAL,
    FAMILY_COLOR,
    INK_2,
    MODEL_FAMILY,
    MODEL_LABEL,
    use_style,
)

matplotlib.use("Agg")
use_style()

_here = Path(__file__).resolve().parent
ROOT = _here if (_here / "experiments").exists() else _here.parent
EXP01 = ROOT / "experiments/01-train-delays/results"
EXP02 = ROOT / "experiments/02-electricity-prices/results"

GITHUB_URL = "https://github.com/Gjusev/forecast-arena"


@cache
def load_predictions(exp_dir: Path) -> pl.DataFrame | None:
    p = exp_dir / "predictions.parquet"
    return pl.read_parquet(p) if p.exists() else None


@cache
def load_metrics(exp_dir: Path, tier: str) -> pl.DataFrame | None:
    p = exp_dir / f"metrics_{tier}.parquet"
    return pl.read_parquet(p) if p.exists() else None


@cache
def load_manifest(exp_dir: Path, tier: str) -> dict:
    p = exp_dir / f"manifest_{tier}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def available_tiers(exp_dir: Path) -> list[str]:
    tiers = [d.stem.split("_")[1] for d in exp_dir.glob("metrics_*.parquet")]
    return sorted(set(tiers), key=["smoke", "pilot", "full"].index)


def _model_color(m: str) -> str:
    return FAMILY_COLOR.get(MODEL_FAMILY.get(m, "baseline"), "#1baf7a")


# ---------------------------------------------------------------- train tab


def train_stations(tier: str) -> list[str]:
    preds = load_predictions(EXP01)
    if preds is None:
        return []
    df = preds.filter(pl.col("tier") == tier)
    return sorted(
        {
            s.split("/")[1]
            for s in df["series_id"].unique().to_list()
            if s.startswith("avg_delay_min")
        }
    )


def train_overview(tier: str):
    metrics = load_metrics(EXP01, tier)
    if metrics is None:
        return "Run `arena run 01 --tier ...` first — no cached results yet.", None
    best = metrics.filter((pl.col("target") == "avg_delay_min") & (pl.col("h") == 1)).sort("mae")
    lines = ["### Train delays — MAE by model (primary target, 1h ahead, all stations)\n"]
    for row in best.iter_rows(named=True):
        skill = row.get("skill_vs_baseline_pct")
        skill_s = f"{'+' if (skill or 0) >= 0 else ''}{skill:.1f}%" if skill is not None else "—"
        lines.append(
            f"- **{MODEL_LABEL.get(row['model'], row['model'])}** — MAE "
            f"{row['mae']:.2f} min · skill vs naive {skill_s}"
        )
    man = load_manifest(EXP01, tier)
    lines.append(
        f"\n*{man.get('n_series', '?')} series · {len(man.get('origins', []))} rolling "
        f"origins · horizon 24h (reported at h=1,3,6,24)*"
    )
    # summary chart
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    models = best["model"].to_list()
    maes = best["mae"].to_list()
    ax.barh(
        np.arange(len(models)), maes, height=0.6, color=[_model_color(m) for m in models], zorder=3
    )
    ax.set_yticks(np.arange(len(models)))
    ax.set_yticklabels([MODEL_LABEL.get(m, m) for m in models])
    ax.invert_yaxis()
    ax.set_xlabel("MAE, minutes (lower is better)")
    ax.set_title("Average arrival delay — 1h ahead, 5 major stations", loc="left")
    ax.grid(axis="y", visible=False)
    return "\n".join(lines), fig


def train_station_plot(tier: str, station: str, model: str):
    preds = load_predictions(EXP01)
    if preds is None or not station:
        return None
    df = preds.filter(
        (pl.col("tier") == tier)
        & (pl.col("series_id") == f"avg_delay_min/{station}")
        & (pl.col("model") == model)
    )
    if df.height == 0:
        return None
    origin = df["origin_ts"].unique().sort()[-1]
    g = df.filter(pl.col("origin_ts") == origin).sort("h")
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    ax.plot(
        g["h"].to_numpy(), g["y_true"].to_numpy(), color=ACTUAL, lw=1.8, zorder=3, label="Actual"
    )
    ax.plot(
        g["h"].to_numpy(),
        g["y_pred"].to_numpy(),
        color=_model_color(model),
        lw=1.8,
        zorder=4,
        label=MODEL_LABEL.get(model, model),
    )
    lo, hi = g["q10"].to_numpy(), g["q90"].to_numpy()
    if np.isfinite(lo.astype(float)).any():
        ax.fill_between(
            g["h"].to_numpy(),
            lo.astype(float),
            hi.astype(float),
            color=_model_color(model),
            alpha=0.15,
            lw=0,
            label="80% interval",
        )
    ax.set_xlabel("hours ahead of forecast origin")
    ax.set_ylabel("avg arrival delay, min")
    ax.set_title(f"{station} — forecast origin {origin}", loc="left")
    ax.legend(frameon=False, fontsize=9)
    return fig


# ----------------------------------------------------------- electricity tab


def elec_overview(tier: str):
    metrics = load_metrics(EXP02, tier)
    if metrics is None:
        return "Run `arena run 02 --tier ...` first — no cached results yet.", None, None
    pooled = (
        metrics.group_by("model")
        .agg(pl.col("mae").mean().alias("mae"), pl.col("coverage_80").mean().alias("cov"))
        .sort("mae")
    )
    lines = ["### Day-ahead prices — MAE pooled over all 24 delivery hours\n"]
    for row in pooled.iter_rows(named=True):
        cov = row.get("cov")
        cov_s = f"{cov * 100:.0f}%" if cov is not None and np.isfinite(cov) else "—"
        lines.append(
            f"- **{MODEL_LABEL.get(row['model'], row['model'])}** — MAE "
            f"{row['mae']:.2f} €/MWh · 80% interval coverage {cov_s}"
        )
    man = load_manifest(EXP02, tier)
    lines.append(
        f"\n*{len(man.get('origins', []))} daily origins · DE-LU day-ahead · "
        f"pre-auction protocol (ADR-0002)*"
    )
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    models = pooled["model"].to_list()
    ax.barh(
        np.arange(len(models)),
        pooled["mae"].to_list(),
        height=0.6,
        color=[_model_color(m) for m in models],
        zorder=3,
    )
    ax.set_yticks(np.arange(len(models)))
    ax.set_yticklabels([MODEL_LABEL.get(m, m) for m in models])
    ax.invert_yaxis()
    ax.set_xlabel("MAE, €/MWh (lower is better)")
    ax.set_title("German day-ahead price forecast — pooled over delivery hours", loc="left")
    ax.grid(axis="y", visible=False)
    # negative-price detection + scheduling summary if available
    neg_summary = "Negative-price detection: computed in the technical report tables."
    return "\n".join(lines), fig, neg_summary


def elec_day_plot(tier: str, model: str):
    preds = load_predictions(EXP02)
    if preds is None:
        return None, None
    df = preds.filter((pl.col("tier") == tier) & (pl.col("model") == model))
    if df.height == 0:
        return None, None
    origin = df["origin_ts"].unique().sort()[-1]
    g = df.filter(pl.col("origin_ts") == origin).sort("h")
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    ax.plot(
        g["h"].to_numpy(),
        g["y_true"].to_numpy(),
        color=ACTUAL,
        lw=1.8,
        zorder=3,
        label="Actual (auction result)",
    )
    ax.plot(
        g["h"].to_numpy(),
        g["y_pred"].to_numpy(),
        color=_model_color(model),
        lw=1.8,
        zorder=4,
        label=MODEL_LABEL.get(model, model),
    )
    lo, hi = g["q10"].to_numpy(), g["q90"].to_numpy()
    if np.isfinite(lo.astype(float)).any():
        ax.fill_between(
            g["h"].to_numpy(),
            lo.astype(float),
            hi.astype(float),
            color=_model_color(model),
            alpha=0.15,
            lw=0,
            label="80% interval",
        )
    ax.axhline(0, color=INK_2, lw=0.8, ls=":")
    ax.set_xlabel("delivery hour of day D")
    ax.set_ylabel("€/MWh")
    ax.set_title(f"DE-LU day-ahead — delivery day {origin}", loc="left")
    ax.legend(frameon=False, fontsize=9)
    # scheduling simulation for this model
    sim = run_simulation(df, model)
    savings = sim["savings_vs_fixed_eur"].mean()
    regret = sim["regret_vs_oracle_eur"].mean()
    txt = (
        f"**Scheduling simulation** (4 MWh flexible load/day, cheapest-4-hours):\n"
        f"- Mean saving vs fixed midday: **{savings:+,.0f} €/day**\n"
        f"- Mean regret vs oracle: **{regret:+,.0f} €/day**\n"
        f"- Wholesale costs only — not a household bill estimate."
    )
    return fig, txt


# -------------------------------------------------------------- comparison


def comparison_table(tier01: str, tier02: str):
    m1, m2 = load_metrics(EXP01, tier01), load_metrics(EXP02, tier02)
    man1, man2 = load_manifest(EXP01, tier01), load_manifest(EXP02, tier02)
    rows = []
    secs1 = man1.get("per_model_seconds") or {}
    secs2 = man2.get("per_model_seconds") or {}
    for m in MODEL_LABEL:
        r = {"Model": MODEL_LABEL[m], "Family": MODEL_FAMILY[m].title()}
        if m1 is not None:
            g = m1.filter(
                (pl.col("model") == m) & (pl.col("target") == "avg_delay_min") & (pl.col("h") == 1)
            )
            r["Delays MAE 1h (min)"] = round(float(g["mae"][0]), 2) if g.height else None
            r["Delays runtime (s)"] = round(secs1.get(m, float("nan")), 1)
        if m2 is not None:
            g = m2.filter(pl.col("model") == m)
            r["Prices MAE (€/MWh)"] = round(float(g["mae"].mean()), 2) if g.height else None
            r["Prices runtime (s)"] = round(secs2.get(m, float("nan")), 1)
        rows.append(r)
    return pl.DataFrame(rows).to_pandas()


def build_app() -> gr.Blocks:
    tiers01 = available_tiers(EXP01)
    tiers02 = available_tiers(EXP02)
    with gr.Blocks(title="forecast-arena — AI vs Reality") as app:
        gr.Markdown(
            """
            # AI vs Reality
            **Real Data. Real Predictions. Real Results.**
            Can time series foundation models beat classical methods on real-world
            forecasting? This dashboard shows cached benchmark results — every number
            traces to a committed predictions file. [Methodology & code on GitHub]("""
            + GITHUB_URL
            + """)
            """
        )
        with gr.Tab("Train delays"):
            with gr.Row():
                tier01_dd = gr.Dropdown(
                    tiers01, value=tiers01[-1] if tiers01 else None, label="Benchmark tier"
                )
                station_dd = gr.Dropdown([], label="Station")
                model01_dd = gr.Dropdown([], label="Model")
            overview01 = gr.Markdown()
            overview_fig01 = gr.Plot()
            station_fig = gr.Plot()
            tier01_dd.change(train_overview, tier01_dd, [overview01, overview_fig01])
            app.load(train_overview, tier01_dd, [overview01, overview_fig01])

            def _fill_station(tier):
                stations = train_stations(tier)
                preds = load_predictions(EXP01)
                models = (
                    sorted(preds.filter(pl.col("tier") == tier)["model"].unique().to_list())
                    if preds is not None
                    else []
                )  # noqa: E501
                return gr.update(
                    choices=stations, value=stations[0] if stations else None
                ), gr.update(choices=models, value=models[0] if models else None)

            tier01_dd.change(_fill_station, tier01_dd, [station_dd, model01_dd])
            station_dd.change(train_station_plot, [tier01_dd, station_dd, model01_dd], station_fig)
            model01_dd.change(train_station_plot, [tier01_dd, station_dd, model01_dd], station_fig)

        with gr.Tab("Electricity prices"):
            with gr.Row():
                tier02_dd = gr.Dropdown(
                    tiers02, value=tiers02[-1] if tiers02 else None, label="Benchmark tier"
                )
                model02_dd = gr.Dropdown([], label="Model")
            overview02 = gr.Markdown()
            overview_fig02 = gr.Plot()
            day_fig = gr.Plot()
            sim_txt = gr.Markdown()
            tier02_dd.change(elec_overview, tier02_dd, [overview02, overview_fig02, sim_txt])
            app.load(elec_overview, tier02_dd, [overview02, overview_fig02, sim_txt])

            def _fill_models(tier):
                preds = load_predictions(EXP02)
                models = (
                    sorted(preds.filter(pl.col("tier") == tier)["model"].unique().to_list())
                    if preds is not None
                    else []
                )  # noqa: E501
                return gr.update(choices=models, value=models[0] if models else None)

            tier02_dd.change(_fill_models, tier02_dd, model02_dd)
            model02_dd.change(elec_day_plot, [tier02_dd, model02_dd], [day_fig, sim_txt])

        with gr.Tab("Comparison"):
            with gr.Row():
                cmp_t1 = gr.Dropdown(
                    tiers01, value=tiers01[-1] if tiers01 else None, label="Delays tier"
                )
                cmp_t2 = gr.Dropdown(
                    tiers02, value=tiers02[-1] if tiers02 else None, label="Electricity tier"
                )
            cmp_df = gr.Dataframe()
            cmp_t1.change(comparison_table, [cmp_t1, cmp_t2], cmp_df)
            cmp_t2.change(comparison_table, [cmp_t1, cmp_t2], cmp_df)
            app.load(comparison_table, [cmp_t1, cmp_t2], cmp_df)
            gr.Markdown(
                "Runtime = wall-clock seconds for all forecasts of the tier on the "
                "development machine (CPU), from the run manifest — hardware-dependent, "
                "compare orders of magnitude, not decimals."
            )
    return app


if __name__ == "__main__":
    build_app().launch()
