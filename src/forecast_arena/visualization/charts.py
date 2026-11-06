"""Publication charts for forecast-arena.

Design contract (validated palette, dataviz method):
- Color encodes MODEL FAMILY, fixed across every chart: foundation=blue,
  ml=orange, baseline=aqua (three all-pairs-safe slots; aqua <3:1 contrast is
  relieved by direct labels + published metric tables).
- 'Actual' data wears neutral ink, never a series color.
- One axis per chart; recessive grid; thin marks; direct labels in text ink.
- Every figure reads ONLY from stored benchmark outputs.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

matplotlib.use("Agg")

FAMILY_COLOR = {
    "foundation": "#2a78d6",  # blue
    "ml": "#eb6834",  # orange
    "baseline": "#1baf7a",  # aqua
}
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_3 = "#8a8984"
GRID = "#e5e4e0"
SURFACE = "#fcfcfb"
ACTUAL = "#0b0b0b"

MODEL_FAMILY = {
    "timestral_28M": "foundation",
    "timestral_209M": "foundation",
    "chronos_2": "foundation",
    "timesfm_3_0": "foundation",
    "lightgbm": "ml",
    "xgboost": "ml",
    "seasonal_naive_24h": "baseline",
    "hour_of_week_climatology": "baseline",
}
MODEL_LABEL = {
    "timestral_28M": "Timestral 28M",
    "timestral_209M": "Timestral 209M",
    "chronos_2": "Chronos-2",
    "timesfm_3_0": "TimesFM 3.0",
    "lightgbm": "LightGBM",
    "xgboost": "XGBoost",
    "seasonal_naive_24h": "Seasonal naive (24h)",
    "hour_of_week_climatology": "Hour-of-week climatology",
}

_STYLE_SET = False


def use_style() -> None:
    global _STYLE_SET
    if _STYLE_SET:
        return
    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "axes.edgecolor": INK_3,
            "axes.labelcolor": INK_2,
            "axes.titlecolor": INK,
            "text.color": INK_2,
            "xtick.color": INK_2,
            "ytick.color": INK_2,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "figure.dpi": 120,
        }
    )
    _STYLE_SET = True


def _save(fig: Path, out_dir: Path, name: str, linkedin: bool = False) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    paths.append(out_dir / f"{name}.png")
    fig.savefig(paths[0], dpi=300, bbox_inches="tight")
    paths.append(out_dir / f"{name}.svg")
    fig.savefig(paths[1], bbox_inches="tight")
    if linkedin:
        # LinkedIn portrait crop: 1080x1350 at 300 dpi.
        li = out_dir / f"{name}_linkedin.png"
        fig.set_size_inches(1080 / 300, 1350 / 300)
        fig.savefig(li, dpi=300, bbox_inches="tight", pad_inches=0.4)
        paths.append(li)
    plt.close(fig)
    return paths


def fig_model_accuracy(
    metrics: pl.DataFrame,
    target: str,
    h: int,
    out_dir: Path,
    title: str,
    baseline: str = "seasonal_naive_24h",
) -> list[Path]:
    """Horizontal bars of MAE per model, family-colored, baseline reference line."""
    use_style()
    df = metrics.filter((pl.col("target") == target) & (pl.col("h") == h)).sort("mae")
    models = df["model"].to_list()
    maes = df["mae"].to_list()
    base_mae = (
        float(df.filter(pl.col("model") == baseline)["mae"][0]) if baseline in models else None
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    y = np.arange(len(models))
    colors = [FAMILY_COLOR[MODEL_FAMILY[m]] for m in models]
    ax.barh(y, maes, height=0.62, color=colors, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([MODEL_LABEL.get(m, m) for m in models])
    if base_mae is not None:
        ax.axvline(base_mae, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=4)
        ax.text(
            base_mae,
            len(models) - 0.28,
            " seasonal naive",
            fontsize=8.5,
            color=INK_2,
            ha="left",
            va="top",
        )
    for yi, mae in zip(y, maes, strict=False):
        ax.text(mae + max(maes) * 0.012, yi, f"{mae:.2f}", va="center", fontsize=9, color=INK_2)
    ax.set_xlabel("MAE (lower is better)")
    ax.set_title(title, loc="left")
    ax.grid(axis="y", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in FAMILY_COLOR.values()]
    ax.legend(
        handles,
        ["Foundation (zero-shot)", "Gradient boosting", "Statistical baseline"],
        loc="lower right",
        frameon=False,
        fontsize=8.5,
    )
    name = f"accuracy_{target}_h{h}"
    return _save(fig, out_dir, name)


def fig_actual_vs_predicted(
    preds: pl.DataFrame,
    series_id: str,
    origin_ts: str,
    out_dir: Path,
    title: str,
) -> list[Path]:
    """Small multiples: one panel per model, actual (neutral) vs predicted."""
    use_style()
    models = [
        m
        for m in MODEL_FAMILY
        if (
            preds.filter(
                (pl.col("series_id") == series_id)
                & (pl.col("origin_ts") == origin_ts)
                & (pl.col("model") == m)
            ).height
            > 0
        )
    ]
    n = len(models)
    if n == 0:
        raise ValueError("no predictions for that series/origin")
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(
        rows, cols, figsize=(4.2 * cols, 2.6 * rows), sharex=True, sharey=True, squeeze=False
    )
    for i, m in enumerate(models):
        ax = axes[i // cols][i % cols]
        g = preds.filter(
            (pl.col("series_id") == series_id)
            & (pl.col("origin_ts") == origin_ts)
            & (pl.col("model") == m)
        ).sort("h")
        hs = g["h"].to_numpy()
        y = g["y_true"].to_numpy().astype(float)
        p = g["y_pred"].to_numpy().astype(float)
        ax.plot(hs, y, color=ACTUAL, lw=1.6, zorder=3, label="Actual")
        ax.plot(hs, p, color=FAMILY_COLOR[MODEL_FAMILY[m]], lw=1.8, zorder=4, label=MODEL_LABEL[m])
        if "q10" in g.columns:
            lo = g["q10"].to_numpy().astype(float)
            hi = g["q90"].to_numpy().astype(float)
            ok = np.isfinite(lo) & np.isfinite(hi)
            if ok.any():
                ax.fill_between(
                    hs[ok], lo[ok], hi[ok], color=FAMILY_COLOR[MODEL_FAMILY[m]], alpha=0.15, lw=0
                )
        ax.set_title(MODEL_LABEL[m], fontsize=9.5, fontweight="normal")
        ax.set_xticks([1, 6, 12, 18, 24])
        if i % cols == 0:
            ax.set_ylabel("value")
        if i // cols == rows - 1:
            ax.set_xlabel("hours ahead" if "delay" in series_id else "delivery hour")
    for j in range(n, rows * cols):
        axes[j // cols][j % cols].set_visible(False)
    fig.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    name = f"actual_vs_pred_{series_id.replace('/', '_')}_{origin_ts[:10]}"
    return _save(fig, out_dir, name.replace(":", "").replace(" ", "_"))


def fig_detection(
    det: pl.DataFrame,
    metric_prefix: str,
    out_dir: Path,
    title: str,
) -> list[Path]:
    """Precision vs recall scatter per model (event detection)."""
    use_style()
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    markers = {"foundation": "o", "ml": "s", "baseline": "^"}
    seen = set()
    for row in det.iter_rows(named=True):
        m = row["model"]
        fam = MODEL_FAMILY.get(m, "baseline")
        prec = row.get(f"{metric_prefix}precision")
        rec = row.get(f"{metric_prefix}recall")
        if prec is None or rec is None or prec is None or not np.isfinite(prec):
            continue
        lbl = MODEL_LABEL.get(m, m)
        ax.scatter(
            rec,
            prec,
            s=90,
            color=FAMILY_COLOR[fam],
            marker=markers[fam],
            zorder=4,
            label=fam if fam not in seen else None,
            edgecolors=SURFACE,
            linewidths=1.5,
        )
        ax.annotate(
            lbl, (rec, prec), textcoords="offset points", xytext=(7, -3), fontsize=8.5, color=INK_2
        )
        seen.add(fam)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(title, loc="left")
    handles = [
        plt.Line2D(
            [],
            [],
            marker=markers[k],
            ls="",
            color=FAMILY_COLOR[k],
            markersize=9,
            label={
                "foundation": "Foundation",
                "ml": "Gradient boosting",
                "baseline": "Statistical",
            }[k],
        )
        for k in FAMILY_COLOR
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8.5)
    return _save(fig, out_dir, f"detection_{metric_prefix.rstrip('_')}")


def fig_accuracy_runtime(
    metrics: pl.DataFrame,
    per_model_seconds: dict[str, float],
    target: str,
    h: int,
    out_dir: Path,
    title: str,
    baseline: str = "seasonal_naive_24h",
) -> list[Path]:
    """Scatter: per-model compute (log x) vs MAE (y). Reference line = baseline MAE."""
    use_style()
    df = metrics.filter((pl.col("target") == target) & (pl.col("h") == h))
    base_mae = float(df.filter(pl.col("model") == baseline)["mae"][0])
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    markers = {"foundation": "o", "ml": "s", "baseline": "^"}
    for row in df.iter_rows(named=True):
        m = row["model"]
        secs = per_model_seconds.get(m, float("nan"))
        mae = row["mae"]
        if not np.isfinite(secs) or not np.isfinite(mae):
            continue
        fam = MODEL_FAMILY.get(m, "baseline")
        ax.scatter(
            max(secs, 0.05),
            mae,
            s=110,
            color=FAMILY_COLOR[fam],
            marker=markers[fam],
            zorder=4,
            edgecolors=SURFACE,
            linewidths=1.5,
        )
        ax.annotate(
            MODEL_LABEL.get(m, m),
            (max(secs, 0.05), mae),
            textcoords="offset points",
            xytext=(8, -3),
            fontsize=8.5,
            color=INK_2,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Total inference + fitting time, seconds (log scale)")
    ax.set_ylabel("MAE (lower is better)")
    ax.axhline(base_mae, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=2)
    ax.text(ax.get_xlim()[0], base_mae * 0.97, "seasonal naive", fontsize=8.5, color=INK_2)
    ax.set_title(title, loc="left")
    handles = [
        plt.Line2D(
            [],
            [],
            marker=markers[k],
            ls="",
            color=FAMILY_COLOR[k],
            markersize=9,
            label={
                "foundation": "Foundation",
                "ml": "Gradient boosting",
                "baseline": "Statistical",
            }[k],
        )
        for k in FAMILY_COLOR
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=8.5)
    return _save(fig, out_dir, f"accuracy_runtime_{target}_h{h}")


def fig_scheduling(
    sim: pl.DataFrame,
    out_dir: Path,
    title: str,
) -> list[Path]:
    """Realized cost per strategy over the simulation window."""
    use_style()
    cols = [
        c
        for c in ["fixed_midday_cost", "yesterday_best_cost", "model_cost", "oracle_cost"]
        if c in sim.columns and sim[c].dtype.is_numeric()
    ]
    means = {c: float(sim[c].mean()) for c in cols}
    order = sorted(means, key=means.get, reverse=True)
    labels = {
        "fixed_midday_cost": "Fixed midday",
        "yesterday_best_cost": "Yesterday's cheapest",
        "model_cost": "Model-scheduled",
        "oracle_cost": "Oracle (perfect foresight)",
    }
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    y = np.arange(len(order))
    colors = [INK_3, INK_3, FAMILY_COLOR["foundation"], ACTUAL]
    ax.barh(y, [means[c] for c in order], height=0.6, color=colors[: len(order)], zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([labels[c] for c in order])
    for yi, c in zip(y, order, strict=False):
        ax.text(means[c] * 1.002, yi, f"{means[c]:,.0f} €", va="center", fontsize=9, color=INK_2)
    ax.set_xlabel("Mean realized cost per day, EUR (4 MWh flexible load, wholesale)")
    ax.set_title(title, loc="left")
    ax.grid(axis="y", visible=False)
    name = "scheduling_cost"
    return _save(fig, out_dir, name, linkedin=True)
