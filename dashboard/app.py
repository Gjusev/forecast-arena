"""forecast-arena dashboard: replay, rank and duel cached benchmark forecasts.

Run:  uv run --extra dashboard python dashboard/app.py   -> http://localhost:7860
Reads only committed artifacts under experiments/*/results (no live inference).
Works on Gradio 5 and 6 (styling kwargs moved from Blocks to launch in 6).
"""

from __future__ import annotations

import json
import random
from datetime import datetime
from functools import cache
from pathlib import Path
from urllib.parse import quote

import gradio as gr
import plotly.graph_objects as go
import polars as pl

from forecast_arena.evaluation.simulation import run_simulation
from forecast_arena.visualization.charts import MODEL_FAMILY, MODEL_LABEL

_here = Path(__file__).resolve().parent
ROOT = _here if (_here / "experiments").exists() else _here.parent
GITHUB_URL = "https://github.com/Gjusev/forecast-arena"

# brand: high-voltage signage on black. AI = signal yellow, reality = paper.
INK, PAPER, DIM, FAINT, SIGNAL = "#0b0b0b", "#f3f1ea", "#8d8a82", "#26251f", "#ffd400"
FAMILY_COLOR = {"foundation": "#2a78d6", "ml": "#eb6834", "baseline": "#1baf7a"}
FAMILY_NAME = {
    "foundation": "Pretrained AI",
    "ml": "Classic machine learning",
    "baseline": "Simple rule",
}
VIDEO = ROOT / "assets/video/forecast-arena.mp4"
SKILL = "Better than 'same as yesterday' (%)"
DASHES = ["solid", "dash", "dot", "dashdot"]

EXPS = {
    "Train delays": {
        "dir": ROOT / "experiments/01-train-delays/results",
        "prefix": "avg_delay_min/",
        "unit": "min",
        "y": "average arrival delay, min",
        "x": "hours after the forecast was made",
        "x_offset": 0,
        "primary_target": "avg_delay_min",
        "by_h": True,
    },
    "Power prices": {
        "dir": ROOT / "experiments/02-electricity-prices/results",
        "prefix": "day_ahead_price/",
        "unit": "€/MWh",
        "y": "day-ahead price, €/MWh",
        "x": "delivery hour (forecast made the morning before)",
        "x_offset": -1,
        "primary_target": "day_ahead_price",
        "by_h": False,
    },
    "Weather": {
        "dir": ROOT / "experiments/03-dwd-weather/results",
        "prefix": "air_temperature/",
        "unit": "°C",
        "y": "2m air temperature, °C",
        "x": "hours after the forecast was made",
        "x_offset": 0,
        "primary_target": "air_temperature",
        "by_h": True,
    },
    "Renewables": {
        "dir": ROOT / "experiments/04-renewables/results",
        "prefix": "",
        "unit": "MW",
        "y": "generation, MW",
        "x": "delivery hour (forecast made the day before)",
        "x_offset": -1,
        "primary_target": "wind_total",
        "by_h": True,
    },
}
REAL_MODELS = [m for m, f in MODEL_FAMILY.items() if f != "baseline"]


def label(m: str) -> str:
    return MODEL_LABEL.get(m, m)


def color(m: str) -> str:
    return FAMILY_COLOR[MODEL_FAMILY.get(m, "baseline")]


def dash(m: str) -> str:
    fam = MODEL_FAMILY.get(m, "baseline")
    same = [k for k, f in MODEL_FAMILY.items() if f == fam]
    return DASHES[same.index(m) % len(DASHES)] if m in same else "solid"


def nice_ts(s: str) -> str:
    try:
        return datetime.fromisoformat(s[:19]).strftime("%a %d %b %Y, %H:%M")
    except ValueError:
        return s


# ------------------------------------------------------------------ data


@cache
def preds(exp: str) -> pl.DataFrame:
    e = EXPS[exp]
    p = pl.read_parquet(e["dir"] / "predictions.parquet")
    tiers = set(p["tier"].unique().to_list())
    tier = next(t for t in ("full", "pilot", "smoke") if t in tiers)
    return p.filter((pl.col("tier") == tier) & pl.col("series_id").str.starts_with(e["prefix"]))


@cache
def metrics(exp: str) -> tuple[pl.DataFrame, str]:
    """Best available tier: full, then pilot, then smoke."""
    for tier in ("full", "pilot", "smoke"):
        f = EXPS[exp]["dir"] / f"metrics_{tier}.parquet"
        if f.exists():
            return pl.read_parquet(f), tier
    return pl.DataFrame(), ""


@cache
def manifest(exp: str) -> dict:
    for tier in ("full", "pilot", "smoke"):
        p = EXPS[exp]["dir"] / f"manifest_{tier}.json"
        if p.exists():
            return json.loads(p.read_text())
    return {}


@cache
def per_origin(exp: str) -> pl.DataFrame:
    """MAE of every model on every single forecast (series x origin)."""
    return (
        preds(exp)
        .filter(pl.col("y_true").is_finite() & pl.col("y_pred").is_finite())
        .group_by("series_id", "origin_ts", "model")
        .agg((pl.col("y_true") - pl.col("y_pred")).abs().mean().alias("mae"))
    )


def series_choices(exp: str) -> list[str]:
    pre = EXPS[exp]["prefix"]
    return sorted(s.removeprefix(pre) for s in preds(exp)["series_id"].unique().to_list())


@cache
def origins(exp: str, series: str) -> list[str]:
    sid = EXPS[exp]["prefix"] + series
    return preds(exp).filter(pl.col("series_id") == sid)["origin_ts"].unique().sort().to_list()


def models_of(exp: str) -> list[str]:
    present = set(preds(exp)["model"].unique().to_list())
    return [m for m in MODEL_LABEL if m in present]


def leaderboard(exp: str, h: int | None) -> pl.DataFrame:
    e = EXPS[exp]
    m, _tier = metrics(exp)
    if m.height == 0:
        return m
    m = m.filter(pl.col("target") == e["primary_target"])
    if e["by_h"]:
        m = m.filter(pl.col("h") == (int(h) if h is not None else 1))
    m = m.group_by("model").agg(
        pl.col("mae").mean(),
        pl.col("skill_vs_baseline_pct").mean().alias("skill"),
        pl.col("coverage_80").mean().alias("coverage"),
    )
    return m.sort("mae")


def best_of(lb: pl.DataFrame, family: str) -> dict:
    fam = lb.filter(pl.col("model").replace_strict(MODEL_FAMILY, default="baseline") == family)
    return fam.sort("mae").row(0, named=True)


# ------------------------------------------------------------------ plot style


def styled(fig: go.Figure, title: str, xlab: str = "", ylab: str = "", h: int = 460) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=h,
        paper_bgcolor=INK,
        plot_bgcolor=INK,
        font={"family": "Barlow, Arial, sans-serif", "color": PAPER, "size": 15},
        title={
            "text": title,
            "x": 0,
            "xanchor": "left",
            "font": {"family": "Barlow Condensed, Arial Narrow, sans-serif", "size": 26},
        },
        margin={"l": 64, "r": 24, "t": 64, "b": 96},
        legend={"orientation": "h", "y": -0.26, "x": 0, "font": {"size": 14}},
        hoverlabel={"font_family": "Barlow, Arial, sans-serif", "bgcolor": "#1a1915"},
        hovermode="x unified",
    )
    fig.update_xaxes(title=xlab, gridcolor=FAINT, zeroline=False, linecolor=FAINT)
    fig.update_yaxes(title=ylab, gridcolor=FAINT, zeroline=False, linecolor=FAINT)
    return fig


# ------------------------------------------------------------------ replay (the live thing)


def replay(exp, series, idx, picked, band, revealed, pick):
    e = EXPS[exp]
    orgs = origins(exp, series)
    if not orgs or not picked:
        return go.Figure(), "Pick at least one model.", ""
    idx = int(min(max(idx, 0), len(orgs) - 1))
    origin = orgs[idx]
    g = preds(exp).filter(
        (pl.col("series_id") == e["prefix"] + series) & (pl.col("origin_ts") == origin)
    )
    fig = go.Figure()
    x_of = lambda d: (d["h"] + e["x_offset"]).to_list()  # noqa: E731
    first = g.filter(pl.col("model") == picked[0]).sort("h")
    if band and first.height and first["q10"].is_finite().any():
        x = x_of(first)
        fig.add_trace(
            go.Scatter(
                x=x + x[::-1],
                y=first["q90"].to_list() + first["q10"].to_list()[::-1],
                fill="toself",
                fillcolor=color(picked[0]),
                opacity=0.18,
                line={"width": 0},
                name=f"80% interval, {label(picked[0])}",
                hoverinfo="skip",
            )
        )
    for m in picked:
        d = g.filter(pl.col("model") == m).sort("h")
        fig.add_trace(
            go.Scatter(
                x=x_of(d),
                y=d["y_pred"].to_list(),
                name=label(m),
                mode="lines",
                line={"color": color(m), "width": 3, "dash": dash(m)},
                hovertemplate="%{y:.1f}",
            )
        )
    x0 = (first["h"].min() if first.height else 1) + e["x_offset"] - 0.5
    fig.add_vline(x=x0, line_color=SIGNAL, line_width=5)
    fig.add_annotation(
        x=x0,
        y=1.02,
        yref="paper",
        text="forecast made",
        showarrow=False,
        xanchor="left",
        font={"color": SIGNAL, "size": 13},
    )
    when = f"Forecast made **{nice_ts(origin)}** · forecast {idx + 1} of {len(orgs)}"
    if not revealed:
        styled(fig, f"{series}: what will happen next?", e["x"], e["y"])
        return fig, HOW_TO_READ_REPLAY, when

    a = g.filter(pl.col("model") == picked[0]).sort("h")
    fig.add_trace(
        go.Scatter(
            x=x_of(a),
            y=a["y_true"].to_list(),
            name="Reality",
            mode="lines+markers",
            line={"color": PAPER, "width": 5},
            marker={"size": 6},
            hovertemplate="%{y:.1f}",
        )
    )
    styled(fig, f"{series}: reality revealed", e["x"], e["y"])
    score = (
        per_origin(exp)
        .filter(
            (pl.col("series_id") == e["prefix"] + series)
            & (pl.col("origin_ts") == origin)
            & pl.col("model").is_in(picked)
        )
        .sort("mae")
    )
    rows = score.rows(named=True)
    story = replay_story(exp, a, g, rows)
    lines = [f"| # | Model | Average miss on this forecast ({e['unit']}) |", "|---|---|---|"]
    lines += [
        f"| {i} | {'**' if i == 1 else ''}{label(r['model'])}{'**' if i == 1 else ''} "
        f"| {r['mae']:.2f} |"
        for i, r in enumerate(rows, 1)
    ]
    verdict = ""
    if pick and rows:
        place = next((i for i, r in enumerate(rows, 1) if label(r["model"]) == pick), None)
        if place == 1:
            verdict = f"### You called it. {pick} won this one.\n"
        elif place:
            verdict = (
                f"### {label(rows[0]['model'])} won. Your pick finished #{place} of {len(rows)}.\n"
            )
    return fig, verdict + story + "\n\n" + "\n".join(lines), when


HOW_TO_READ_REPLAY = """**How to read this.** The **yellow line** is the moment the forecast was made.
Each coloured line is one model's guess for what comes next (trains: the next 24 hours;
power: every hour of the next day). The shaded band is the range the first model was
80% sure about. **Reality is still hidden.** Pick the model you think will stay closest,
then press **Reveal reality**."""


def when_label(exp: str, x: int) -> str:
    return f"{x} h after the forecast" if exp == "Train delays" else f"at {x:02d}:00"


def replay_story(exp, actual: pl.DataFrame, g: pl.DataFrame, rows: list[dict]) -> str:
    """One plain-language paragraph about what happened on this forecast."""
    if not rows:
        return ""
    unit, best = EXPS[exp]["unit"], rows[0]
    b = g.filter(pl.col("model") == best["model"]).sort("h")
    d = actual.select("h", "y_true").join(b.select("h", "y_pred"), on="h")
    d = d.filter(pl.col("y_true").is_finite()).with_columns(
        (pl.col("y_true") - pl.col("y_pred")).abs().alias("gap")
    )
    if d.height == 0:
        return ""
    worst = d.sort("gap", descending=True).row(0, named=True)
    x = worst["h"] + EXPS[exp]["x_offset"]
    txt = (
        f"**What happened.** The white line is reality. **{label(best['model'])}** stayed "
        f"closest: on average its guess was {best['mae']:.1f} {unit} away from reality per hour."
    )
    if len(rows) > 1:
        txt += f" {label(rows[-1]['model'])} was furthest off ({rows[-1]['mae']:.1f} {unit})."
    txt += (
        f" The biggest surprise came {when_label(exp, x)}: reality was "
        f"{worst['y_true']:.1f} {unit}, while {label(best['model'])} expected {worst['y_pred']:.1f}."
    )
    return txt


def jump(exp, series, how):
    orgs = origins(exp, series)
    if how == "random":
        return random.randrange(len(orgs))
    po = per_origin(exp).filter(
        (pl.col("series_id") == EXPS[exp]["prefix"] + series) & pl.col("model").is_in(REAL_MODELS)
    )
    by = po.group_by("origin_ts").agg(pl.col("mae").mean()).sort("mae", descending=how == "hard")
    return orgs.index(by["origin_ts"][0])


# ------------------------------------------------------------------ leaderboard


def board(exp, h, metric):
    lb = leaderboard(exp, h if EXPS[exp]["by_h"] else None)
    if lb.height == 0:
        empty = pl.DataFrame({"Model": [], "Family": []})
        return go.Figure(), empty, "No results for this experiment yet - run the benchmark first."
    if metric == SKILL:
        lb = lb.sort("skill", descending=True)
        vals, fmt, xlab = (
            lb["skill"].to_list(),
            "{:+.1f}%",
            "how much smaller the miss is than 'same as yesterday', % (longer bar = better)",
        )
    else:
        vals, fmt, xlab = (
            lb["mae"].to_list(),
            "{:.2f}",
            f"average miss, {EXPS[exp]['unit']} (shorter bar = better)",
        )
    names = [label(m) for m in lb["model"].to_list()]
    fig = go.Figure(
        go.Bar(
            x=vals,
            y=names,
            orientation="h",
            marker_color=[color(m) for m in lb["model"].to_list()],
            text=[fmt.format(v) for v in vals],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    title = (
        f"{exp}, {int(h)} h ahead" if EXPS[exp]["by_h"] else f"{exp}, pooled over 24 delivery hours"
    )
    styled(fig, title, xlab, "", h=440).update_layout(hovermode="closest", showlegend=False)

    secs = manifest(exp).get("per_model_seconds") or {}
    table = pl.DataFrame(
        {
            "Model": names,
            "Family": [FAMILY_NAME[MODEL_FAMILY.get(m, "baseline")] for m in lb["model"].to_list()],
            f"Average miss ({EXPS[exp]['unit']})": lb["mae"].round(2).to_list(),
            "Better than 'same as yesterday'": [f"{v:+.1f}%" for v in lb["skill"].to_list()],
            "Reality inside the 80% range": [
                f"{c:.0%}" if c == c and c is not None else "—" for c in lb["coverage"].to_list()
            ],
            "Compute time (s, CPU)": [
                round(secs[m], 1) if m in secs else None for m in lb["model"].to_list()
            ],
        }
    )
    return fig, table.to_pandas(), board_story(exp, lb, h)


def board_story(exp: str, lb: pl.DataFrame, h) -> str:
    unit = EXPS[exp]["unit"]
    best = lb.sort("mae").row(0, named=True)
    naive = lb.filter(pl.col("model") == "seasonal_naive_24h").row(0, named=True)
    fm, gb = best_of(lb, "foundation"), best_of(lb, "ml")
    if exp == "Weather":
        return (
            f"**In plain words.** Predicting the temperature {int(h)} hour{'s' if int(h) > 1 else ''} ahead at 30 German "
            f"city stations, the best model (**{label(best['model'])}**) misses by "
            f"**{best['mae']:.2f} {unit}** on average; simply repeating yesterday's value for "
            f"this hour misses by {naive['mae']:.2f}. The average hides what matters most: heat "
            "and frost hours. How often models catch those is in the technical report."
        )
    if exp == "Renewables":
        return (
            f"**In plain words.** Predicting tomorrow's wind and solar output, the best model "
            f"(**{label(best['model'])}**) misses by **{best['mae']:.0f} {unit}** on average; "
            f"repeating yesterday's output misses by {naive['mae']:.0f}. For scale, the whole "
            f"German wind fleet reaches about 50,000 MW at full blast."
        )
    if exp == "Train delays":
        ahead = f"{int(h)} hour{'s' if int(h) > 1 else ''} ahead"
        return (
            f"**In plain words.** Forecasting {ahead}, the best model "
            f"(**{label(best['model'])}**) misses the real average delay by "
            f'**{best["mae"]:.2f} {unit}** on average. The simple rule "same as yesterday at '
            f'this hour" misses by {naive["mae"]:.2f}, so the best model is '
            f"{best['skill']:.0f}% more accurate. The best pretrained AI model and the best "
            f"classic machine-learning model are only **{abs(gb['mae'] - fm['mae']):.2f} {unit}** "
            "apart: practically a tie."
        )
    return (
        f"**In plain words.** The best model (**{label(best['model'])}**) misses the real "
        f"electricity price by **{best['mae']:.1f} {unit}** on average; simply repeating "
        f"yesterday's prices misses by {naive['mae']:.1f}. Pretrained AI models are about "
        f"**{fm['skill']:.0f}%** more accurate than repeating yesterday, classic machine "
        f"learning only **{gb['skill']:.0f}%**. Here AI wins clearly."
    )


# ------------------------------------------------------------------ head to head


def duel(exp, a_label, b_label):
    inv = {label(m): m for m in models_of(exp)}
    a, b = inv.get(a_label), inv.get(b_label)
    if not a or not b or a == b:
        return go.Figure(), "Pick two different models."
    po = per_origin(exp)
    j = po.filter(pl.col("model") == a).join(
        po.filter(pl.col("model") == b), on=["series_id", "origin_ts"], suffix="_b"
    )
    n = j.height
    wins = int((j["mae"] < j["mae_b"]).sum())
    hi = float(max(j["mae"].quantile(0.99), j["mae_b"].quantile(0.99)))
    fig = go.Figure()
    for name, mask, c in [
        (f"{a_label} wins", j["mae"] < j["mae_b"], color(a)),
        (f"{b_label} wins", j["mae"] >= j["mae_b"], color(b) if color(b) != color(a) else PAPER),
    ]:
        d = j.filter(mask)
        fig.add_trace(
            go.Scatter(
                x=d["mae"].to_list(),
                y=d["mae_b"].to_list(),
                mode="markers",
                name=name,
                marker={"color": c, "size": 7, "opacity": 0.75},
                text=[nice_ts(o) for o in d["origin_ts"].to_list()],
                hovertemplate="%{text}<br>"
                + a_label
                + ": %{x:.2f}<br>"
                + b_label
                + ": %{y:.2f}<extra></extra>",
            )
        )
    fig.add_shape(
        type="line", x0=0, y0=0, x1=hi, y1=hi, line={"color": DIM, "width": 2, "dash": "dot"}
    )
    unit = EXPS[exp]["unit"]
    styled(
        fig,
        "Every forecast is one dot",
        f"{a_label}: average miss ({unit})",
        f"{b_label}: average miss ({unit})",
        h=520,
    )
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(range=[0, hi], constrain="domain").update_yaxes(
        range=[0, hi], constrain="domain"
    )
    share = wins / n if n else 0
    leader, pct = (a_label, share) if share >= 0.5 else (b_label, 1 - share)
    md = (
        f"## {leader} was closer to reality in {pct:.0%} of {n:,} forecasts\n"
        f"On average {a_label} missed by {j['mae'].mean():.2f} {unit} and {b_label} by "
        f"{j['mae_b'].mean():.2f}. **How to read the chart:** each dot is one forecast. "
        f"Dots above the dotted line are forecasts where {a_label} was closer; below it, "
        f"{b_label} was closer. Hover a dot to see the date."
    )
    return fig, md


# ------------------------------------------------------------------ scheduling


@cache
def sim(model: str) -> pl.DataFrame:
    p = preds("Power prices")
    return run_simulation(p.filter(pl.col("model") == model), model).sort("origin_ts")


def scheduling(chosen):
    if not chosen:
        return go.Figure(), None, ""
    inv = {label(m): m for m in models_of("Power prices")}
    fig, rows = go.Figure(), []
    oracle_sim = sim(inv[chosen[0]])
    oracle_cum = (oracle_sim["fixed_midday_cost"] - oracle_sim["oracle_cost"]).cum_sum()
    dates = [o[:10] for o in oracle_sim["origin_ts"].to_list()]
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=oracle_cum.to_list(),
            name="Knowing the future (best possible)",
            line={"color": PAPER, "width": 2, "dash": "dot"},
        )
    )
    for name in chosen:
        m = inv[name]
        s = sim(m)
        fig.add_trace(
            go.Scatter(
                x=[o[:10] for o in s["origin_ts"].to_list()],
                y=s["savings_vs_fixed_eur"].cum_sum().to_list(),
                name=name,
                line={"color": color(m), "width": 3, "dash": dash(m)},
            )
        )
        save = s["savings_vs_fixed_eur"].mean()
        avail = (s["fixed_midday_cost"] - s["oracle_cost"]).mean()
        rows.append(
            {
                "Model": name,
                "Saving €/day": round(save, 1),
                "Share of the best possible saving": f"{save / avail:.0%}",
                "Days it beat 'always at midday'": f"{(s['savings_vs_fixed_eur'] > 0).mean():.0%}",
                "_fixed": s["fixed_midday_cost"].mean(),
                "_model": s["model_cost"].mean(),
                "_oracle": avail,
                "_n": s.height,
            }
        )
    styled(fig, "Money saved vs always using power at midday", "", "€ saved, adding up", h=480)
    df = pl.DataFrame(rows).sort("Saving €/day", descending=True)
    top = df.row(0, named=True)
    story = (
        "**In plain words.** Imagine a factory, an electric-bus depot or a big battery that "
        "must use 4 MWh of electricity every day but can choose the hours. Always using it at "
        f"midday cost {top['_fixed']:.0f} € a day on average. Following **{top['Model']}**'s "
        f"forecast cut that to {top['_model']:.0f} €: **{top['Saving €/day']:.1f} € saved per "
        f"day**, about {top['Saving €/day'] * top['_n']:,.0f} € over {top['_n']:,} days. "
        f"Knowing the future perfectly would have saved {top['_oracle']:.1f} € a day, so the "
        f"forecast captured **{top['Share of the best possible saving']}** of what was possible. "
        "Wholesale prices only: a home bill adds taxes and grid fees."
    )
    return fig, df.drop([c for c in df.columns if c.startswith("_")]).to_pandas(), story


# ------------------------------------------------------------------ layout

MARK = (
    (ROOT / "assets/brand/mark.svg").read_text()
    if (ROOT / "assets/brand/mark.svg").exists()
    else ""
)

HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
"""

CSS = f"""
:root, .dark {{ --fa-ink:{INK}; --fa-paper:{PAPER}; --fa-signal:{SIGNAL}; --fa-dim:{DIM}; }}
body, gradio-app, .gradio-container, .main, .wrap {{ background:{INK} !important; }}
.gradio-container {{ margin: 0 auto !important; max-width: 1440px !important; width: 100% !important;
  font-family: Barlow, Arial, sans-serif !important; color:{PAPER}; }}
.gradio-container h1, .gradio-container h2, .gradio-container h3 {{ font-family:"Barlow Condensed", Arial Narrow, sans-serif; letter-spacing:-0.01em; }}
#fa-hero {{ padding: 24px 0 8px; }}
#fa-hero .bar {{ display:flex; align-items:center; gap:14px; font-family:"Barlow Condensed"; font-weight:700; font-size:22px; }}
#fa-hero .bar svg {{ width:40px; height:40px; }}
#fa-hero .bar a {{ margin-left:auto; color:{PAPER}; text-decoration:none; font-family:Barlow; font-weight:500; font-size:16px; }}
#fa-hero .bar a:hover, #fa-hero .bar a:focus-visible {{ color:{SIGNAL}; }}
#fa-hero h1 {{ font-size: clamp(56px, 9vw, 132px); line-height:.88; margin: 28px 0 14px; font-weight:800; color:{PAPER}; }}
#fa-hero h1 span {{ color:{SIGNAL}; }}
#fa-hero p.lede {{ font-size: 20px; max-width: 62ch; line-height:1.5; margin:0 0 28px; }}
#fa-hero .verdicts {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 2px; background:{FAINT}; }}
#fa-hero .v {{ background:#14130f; padding: 20px 22px; }}
#fa-hero .v b {{ display:block; font-family:"Barlow Condensed"; font-weight:800; font-size: 46px; line-height:1; color:{SIGNAL}; }}
#fa-hero .v strong {{ display:block; font-size:18px; margin: 10px 0 4px; }}
#fa-hero .v span {{ color:{PAPER}; font-size:16px; line-height:1.45; }}
@media (max-width: 760px) {{ #fa-hero .verdicts {{ grid-template-columns: 1fr; }} }}
table, td, th {{ font-variant-numeric: tabular-nums; }}
.fa-note {{ color:{DIM}; font-size:15px; }}
.fa-explain {{ background:#1d1c17; border-left:6px solid {SIGNAL} !important; padding:16px 20px !important; font-size:18px; line-height:1.55; }}
.fa-explain .fa-explain {{ border-left:0 !important; padding:0 !important; background:none; }}
.fa-explain p {{ font-size:18px !important; line-height:1.55 !important; }}
#fa-start p, #fa-start li {{ font-size:19px; line-height:1.6; max-width:72ch; }}
#fa-start h2 {{ font-size:40px; margin-top:28px; }}
button.primary {{ background:{SIGNAL} !important; color:{INK} !important; border:0 !important; font-weight:600; }}
button.primary:hover {{ filter: brightness(1.08); }}
button.primary:active {{ transform: translateY(1px); }}
@media (max-width: 640px) {{
  #fa-hero h1 {{ font-size: clamp(44px, 15vw, 72px); margin: 20px 0 10px; }}
  #fa-hero .bar {{ flex-wrap: wrap; font-size: 19px; }}
  #fa-hero .bar svg {{ width: 30px; height: 30px; }}
  #fa-hero .bar a {{ margin-left: 0; flex-basis: 100%; }}
  #fa-hero p.lede {{ font-size: 17px; }}
  #fa-hero .v {{ padding: 16px; }}
  #fa-hero .v b {{ font-size: 38px; }}
  #fa-hero .v strong {{ font-size: 16px; }}
  #fa-hero .v span {{ font-size: 15px; }}
  #fa-start p, #fa-start li {{ font-size: 16px; }}
  #fa-start h2 {{ font-size: 28px; margin-top: 20px; }}
  .fa-explain {{ padding: 12px 14px !important; }}
  .fa-explain, .fa-explain p {{ font-size: 16px !important; line-height: 1.5 !important; }}
  .gradio-container .tabitem {{ padding: 0 4px; }}
}}
footer {{ display:none !important; }}
"""

THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.yellow,
    neutral_hue=gr.themes.colors.stone,
    font=[gr.themes.GoogleFont("Barlow"), "Arial", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Barlow"), "Arial", "sans-serif"],
    radius_size=gr.themes.sizes.radius_none,
).set(
    body_background_fill=INK,
    body_background_fill_dark=INK,
    body_text_color=PAPER,
    body_text_color_dark=PAPER,
    block_background_fill="#14130f",
    block_background_fill_dark="#14130f",
    block_border_color=FAINT,
    block_border_color_dark=FAINT,
    block_label_text_color=PAPER,
    block_label_text_color_dark=PAPER,
    block_title_text_color=PAPER,
    block_title_text_color_dark=PAPER,
    input_background_fill="#1d1c17",
    input_background_fill_dark="#1d1c17",
    border_color_primary=FAINT,
    border_color_primary_dark=FAINT,
    color_accent=SIGNAL,
    color_accent_soft="#3d3406",
    color_accent_soft_dark="#3d3406",
    slider_color=SIGNAL,
    slider_color_dark=SIGNAL,
    checkbox_background_color_selected=SIGNAL,
    checkbox_background_color_selected_dark=SIGNAL,
    button_secondary_background_fill="#26251f",
    button_secondary_background_fill_dark="#26251f",
    button_secondary_text_color=PAPER,
    button_secondary_text_color_dark=PAPER,
    table_even_background_fill="#14130f",
    table_even_background_fill_dark="#14130f",
    table_odd_background_fill="#1a1915",
    table_odd_background_fill_dark="#1a1915",
)


def hero_html() -> str:
    d = leaderboard("Train delays", 1)
    p = leaderboard("Power prices", None)
    fm_d, gb_d = best_of(d, "foundation"), best_of(d, "ml")
    fm_p, gb_p = best_of(p, "foundation"), best_of(p, "ml")
    sched_p = EXPS["Power prices"]["dir"] / "report_assets_full/scheduling.json"
    sched = json.loads(sched_p.read_text()) if sched_p.exists() else None
    money = (
        f"""<div class="v"><b>−{sched["savings_vs_fixed_eur"]:.1f} €/day</b>
        <strong>Money: forecasts pay</strong><span>Saved by moving 4 MWh of daily
        electricity use to the hours {label(sched["best_model"])} predicts are cheapest,
        averaged over {sched["n_days"]:,} days. Wholesale prices only.</span></div>"""
        if sched
        else ""
    )
    return f"""
<div id="fa-hero">
  <div class="bar">{MARK}<span>forecast-arena</span>
    <a href="{GITHUB_URL}" target="_blank" rel="noopener">Code, data and reports on GitHub →</a></div>
  <h1><span>AI</span> vs Reality</h1>
  <p class="lede">Do the new pretrained AI forecasting models predict the real world better
  than classic methods? We replayed nearly 2,000 forecasts of German train delays and
  electricity prices, giving every model exactly the same information. New here? Start with
  the 33-second film below.</p>
  <div class="verdicts">
    <div class="v"><b>{gb_d["mae"] - fm_d["mae"]:.2f} min</b><strong>Trains: a tie</strong>
      <span>The best AI model ({label(fm_d["model"])}) misses by {fm_d["mae"]:.2f} min on
      average, the best classic model ({label(gb_d["model"])}) by {gb_d["mae"]:.2f}.</span></div>
    <div class="v"><b>{fm_p["skill"]:+.0f}% vs {gb_p["skill"]:+.0f}%</b><strong>Electricity prices: AI wins</strong>
      <span>How much smaller the miss is than simply repeating yesterday's prices: AI
      ({label(fm_p["model"])}) vs classic ({label(gb_p["model"])}), over
      {len(manifest("Power prices").get("origins", [])):,} days.</span></div>
    {money}
  </div>
</div>"""


def video_html() -> str:
    """Native <video>: muted autoplay loop with the banner as poster (Gradio's player
    neither autoplays reliably nor shows a poster)."""
    url = lambda f: "/gradio_api/file=" + quote(f.resolve().as_posix())  # noqa: E731
    poster = ROOT / "assets/brand/banner.png"
    poster_attr = f' poster="{url(poster)}"' if poster.exists() else ""
    return (
        f'<video src="{url(VIDEO)}"{poster_attr} autoplay muted loop playsinline controls '
        'aria-label="33-second film summarising the results" '
        'style="width:100%;display:block;background:#0b0b0b"></video>'
    )


def start_story() -> str:
    d, p = leaderboard("Train delays", 1), leaderboard("Power prices", None)
    fm_d, gb_d = best_of(d, "foundation"), best_of(d, "ml")
    fm_p, gb_p = best_of(p, "foundation"), best_of(p, "ml")
    # the single worst hour in the train test window, and what the models expected
    t = preds("Train delays").filter((pl.col("h") == 1) & pl.col("y_true").is_finite())
    peak = (
        t.filter(pl.col("model") == "timestral_209M")
        .sort("y_true", descending=True)
        .row(0, named=True)
    )
    guesses = t.filter(
        (pl.col("series_id") == peak["series_id"])
        & (pl.col("origin_ts") == peak["origin_ts"])
        & pl.col("model").is_in(REAL_MODELS)
    )["y_pred"]
    station = peak["series_id"].split("/", 1)[1].replace("(Main)", " (Main) ")
    n = sum(per_origin(e).select("series_id", "origin_ts").unique().height for e in EXPS)
    sched_p = EXPS["Power prices"]["dir"] / "report_assets_full/scheduling.json"
    money = ""
    if sched_p.exists():
        sc = json.loads(sched_p.read_text())
        share = sc["savings_vs_fixed_eur"] / (sc["fixed_midday_cost"] - sc["oracle_cost"])
        money = (
            "**3. It is worth real money.** A business that must use 4 MWh of electricity a day "
            "but can choose the hours, and follows the AI forecast to pick the cheapest ones, "
            f"saves **{sc['savings_vs_fixed_eur']:.0f} € a day** compared with always running "
            f"at midday. That is {share:.0%} of what perfect knowledge of the future would save.\n\n"
        )
    return f"""## The question
New **pretrained AI** forecasting models (the same idea as ChatGPT, but trained on millions of
number series instead of text) promise to predict almost anything without extra training.
Do they really beat older, simpler methods on messy real-world data?

## How we tested it, fairly
We picked two things Germany runs on: **train delays** at five big stations and
**wholesale electricity prices**. Then we went back in time and made **{n:,} forecasts**.
Each time, every model saw exactly the same past data and made its prediction; only then
did we compare it with what really happened. No model could peek at the future.

## What we found
**1. Trains: a tie, and nobody sees a disruption coming.** All serious models were about
{fm_d["skill"]:.0f}% more accurate than the simple rule "same as yesterday at this hour". But
the best AI model and the best classic machine-learning model were only
{abs(gb_d["mae"] - fm_d["mae"]):.2f} minutes apart. When {station} suddenly hit
**{peak["y_true"]:.0f} minutes** of average delay (the hour after {nice_ts(peak["origin_ts"])}), every model
had expected between {guesses.min():.1f} and {guesses.max():.1f}.

**2. Electricity prices: AI wins clearly.** Pretrained AI models were about
**{fm_p["skill"]:.0f}%** more accurate than repeating yesterday's prices; classic machine
learning only **{gb_p["skill"]:.0f}%**. AI was also far better at spotting hours when prices go
**below zero**, which happens when there is so much wind and sun that producers pay to get rid
of power.

{money}**4. The honest catch.** AI is not magic. On trains it was no better than models trained
in seconds on a laptop, and no model predicts sudden disruptions from history alone.

**5. New in the arena.** German weather stations (30 cities, hourly temperature) and
wind + solar generation are now benchmarked with the same protocol - early results are in
the Leaderboard and Replay tabs.

Try it yourself in **Replay a forecast**: pick a moment, bet on a model, reveal reality.
"""


GLOSSARY_MD = """
- **Forecast**: a prediction of a future value, made at one specific moment (the yellow line).
- **Pretrained AI (foundation model)**: Timestral 28M and 209M (Mistral), Chronos-2 (Amazon),
  TimesFM 3.0 (Google). Trained once on huge collections of time series and used here as-is,
  without retraining on this data ("zero-shot").
- **Classic machine learning**: LightGBM and XGBoost. Retrained on this data before every
  forecast; fast, runs on a laptop.
- **Simple rules (baselines)**: "same as yesterday at this hour" (seasonal naive) and "the
  typical value for this hour of the week" (climatology). A useful model must beat them.
- **Average miss (MAE)**: how far a prediction is from reality, on average. 1.8 minutes means
  typically off by about 1.8 minutes.
- **Better than 'same as yesterday' (%)**: how much smaller the average miss is than the
  simple rule. +33% means the miss is a third smaller.
- **80% range**: the band a model says reality will fall into 8 times out of 10. A good model's
  band really does contain reality about 80% of the time.
- **Negative price**: hours with so much wind and solar power that sellers pay buyers to take
  electricity.
- **€/MWh**: euros per megawatt-hour, the wholesale unit. One MWh is roughly a third of what a
  typical German household uses in a year.
"""


METHOD_MD = """
## How the arena works
- **Rolling origins.** Forecasts are replayed chronologically; every model sees exactly the
  same history, truncated at the moment the forecast is made. No shuffling, no peeking.
- **Trains** ([ADR-0001](https://github.com/Gjusev/forecast-arena/blob/main/docs/adr/0001-completed-hour-forecasting-protocol.md)):
  hourly average arrival delay at 5 hub stations, forecast 1 to 24 hours ahead from completed hours.
- **Power** ([ADR-0002](https://github.com/Gjusev/forecast-arena/blob/main/docs/adr/0002-pre-auction-day-ahead-protocol.md)):
  forecasts made at 10:00 the day before, ahead of the day-ahead auction, for all 24 delivery hours.
- **Foundation models run zero-shot** (Timestral 28M/209M, Chronos-2, TimesFM 3.0);
  gradient boosting (LightGBM, XGBoost) is retrained at every origin on lag and calendar features.
- **Thresholds frozen on training data** before any test forecast was scored.

Data: [piebro/deutsche-bahn-data](https://huggingface.co/datasets/piebro/deutsche-bahn-data) (CC-BY-4.0),
[SMARD](https://www.smard.de) Bundesnetzagentur (dl-de/by-2-0). Everything on this page is read
from committed result files; nothing is inferred live.
"""


def _fetch_live(name: str) -> dict | None:
    """Live JSONs: GitHub raw first (always fresh), local live/ as fallback."""
    import urllib.request

    try:
        with urllib.request.urlopen(
            f"https://raw.githubusercontent.com/Gjusev/forecast-arena/main/live/{name}", timeout=10
        ) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        local = ROOT / "live" / name
        if local.exists():
            return json.loads(local.read_text(encoding="utf-8"))
    return None


def live_view():
    pend = _fetch_live("pending.json")
    scores = _fetch_live("scores.json")
    if not pend or pend.get("status") != "pending":
        note = (pend or {}).get("note") or "No live forecast published yet."
        note += (
            " The daily workflow publishes at 00:45 CET; "
            "the auction it predicts runs at 12:00 and publishes ~12:45."
        )
        return None, note
    e = EXPS["Power prices"]
    fig = go.Figure()
    band_added = False
    for m in sorted(pend["forecasts"]):
        d = pend["forecasts"][m]
        fig.add_trace(
            go.Scatter(
                x=list(range(24)),
                y=d["point"],
                name=label(m),
                mode="lines",
                line={"color": color(m), "width": 3, "dash": dash(m)},
                hovertemplate="%{y:.1f}",
            )
        )
        if not band_added and d["q10"] and d["q10"][0] is not None:
            x = list(range(24))
            fig.add_trace(
                go.Scatter(
                    x=x + x[::-1],
                    y=d["q90"] + d["q10"][::-1],
                    fill="toself",
                    fillcolor=color(m),
                    opacity=0.15,
                    line={"width": 0},
                    name=f"80% range, {label(m)}",
                    hoverinfo="skip",
                )
            )
            band_added = True
    styled(
        fig,
        f"Delivery day {pend['delivery_day']}: tomorrow's prices, forecast before the auction",
        e["x"],
        e["y"],
        h=470,
    )
    md = (
        f"**Published {pend['published_utc']}** - committed to GitHub before the 12:00 CET "
        "auction (results ~12:45). The models saw only prices up to the day before delivery."
    )
    if scores and scores.get("scored"):
        rows = scores["leaderboard"]
        head = chr(10).join(
            [
                "",
                "## Score so far",
                "",
                "| Model | Mean miss (EUR/MWh) | Days | 80% range held |",
                "|---|---|---|---|",
            ]
        )
        body = []
        for r in rows:
            cov = f"{r['coverage_80']:.0%}" if r.get("coverage_80") is not None else "-"
            body.append(f"| {label(r['model'])} | {r['mean_mae']} | {r['n']} | {cov} |")
        md += head + chr(10).join(body)
        md += chr(10)
        md += "Each forecast is scored once its delivery day is published. Single days vary a lot; the mean is the real signal."
    return fig, md


def build_app(style_kwargs: dict | None = None) -> gr.Blocks:
    exps = list(EXPS)
    with gr.Blocks(title="forecast-arena — AI vs Reality", **(style_kwargs or {})) as app:
        gr.HTML(hero_html())

        with gr.Tab("Start here"):
            if VIDEO.exists():
                gr.HTML(video_html())
            gr.Markdown(start_story(), elem_id="fa-start")
            with gr.Accordion("Glossary: every term on this page in plain words", open=False):
                gr.Markdown(GLOSSARY_MD)

        with gr.Tab("Live"):
            li_plot = gr.Plot(show_label=False)
            li_md = gr.Markdown()
            gr.Button("Refresh").click(live_view, None, [li_plot, li_md])
            app.load(live_view, None, [li_plot, li_md])

        with gr.Tab("Replay a forecast"):
            gr.Markdown(
                "Pick a moment, choose your contenders, call the winner. Then reveal what really happened."
            )
            with gr.Row():
                r_exp = gr.Radio(exps, value=exps[0], label="Experiment", scale=2)
                r_series = gr.Dropdown(
                    series_choices(exps[0]),
                    value=series_choices(exps[0])[0],
                    label="Station / market",
                    scale=2,
                )
            orgs0 = origins(exps[0], series_choices(exps[0])[0])
            r_idx = gr.Slider(
                0,
                len(orgs0) - 1,
                value=len(orgs0) - 1,
                step=1,
                label="Forecast (scrub through time)",
            )
            r_when = gr.Markdown()
            with gr.Row():
                b_hard = gr.Button("Hardest forecast", size="sm")
                b_easy = gr.Button("Easiest forecast", size="sm")
                b_rand = gr.Button("Surprise me", size="sm")
            default_models = ["timestral_209M", "chronos_2", "lightgbm", "seasonal_naive_24h"]
            r_models = gr.CheckboxGroup(
                [label(m) for m in models_of(exps[0])],
                value=[label(m) for m in default_models],
                label="Contenders",
            )
            with gr.Row():
                r_pick = gr.Radio(
                    [label(m) for m in default_models],
                    label="Your call: who wins this one?",
                    scale=3,
                )
                r_band = gr.Checkbox(value=True, label="Show 80% interval", scale=1, min_width=200)
                b_reveal = gr.Button("Reveal reality", variant="primary", scale=1)
            revealed = gr.State(False)
            r_plot = gr.Plot(show_label=False)
            r_score = gr.Markdown(elem_classes="fa-explain")

            def _models(exp, names):
                inv = {label(m): m for m in models_of(exp)}
                return [inv[n] for n in names if n in inv]

            def render(exp, series, idx, names, band, rev, pick):
                return replay(exp, series, idx, _models(exp, names), band, rev, pick)

            outs = [r_plot, r_score, r_when]
            ins = [r_exp, r_series, r_idx, r_models, r_band, revealed, r_pick]

            def on_exp(exp):
                s = series_choices(exp)
                n = len(origins(exp, s[0]))
                return (
                    gr.update(choices=s, value=s[0]),
                    gr.update(maximum=n - 1, value=n - 1),
                    gr.update(choices=[label(m) for m in models_of(exp)]),
                )

            def on_series(exp, series):
                n = len(origins(exp, series))
                return gr.update(maximum=n - 1, value=n - 1)

            hide = lambda: False  # noqa: E731
            r_exp.change(on_exp, r_exp, [r_series, r_idx, r_models])
            r_series.change(on_series, [r_exp, r_series], r_idx)
            r_models.change(lambda n: gr.update(choices=n, value=None), r_models, r_pick)
            for comp in (r_idx, r_series, r_exp):
                comp.change(hide, None, revealed).then(render, ins, outs)
            for comp in (r_models, r_band):
                comp.change(render, ins, outs)
            for btn, how in ((b_hard, "hard"), (b_easy, "easy"), (b_rand, "random")):
                btn.click(lambda e, s, h=how: jump(e, s, h), [r_exp, r_series], r_idx)
            b_reveal.click(lambda: True, None, revealed).then(render, ins, outs)
            app.load(render, ins, outs)

        with gr.Tab("Leaderboard"):
            with gr.Row():
                l_exp = gr.Radio(exps, value=exps[0], label="Experiment")
                l_h = gr.Radio(["1", "3", "6", "24"], value="1", label="Hours ahead")
                l_metric = gr.Radio(["Average miss", SKILL], value="Average miss", label="Rank by")
            l_story = gr.Markdown(elem_classes="fa-explain")
            l_plot = gr.Plot(show_label=False)
            l_table = gr.Dataframe(interactive=False)
            gr.Markdown(
                "Runtime is wall-clock seconds for every forecast of the run on one CPU; "
                "compare orders of magnitude, not decimals.",
                elem_classes="fa-note",
            )
            l_outs = [l_plot, l_table, l_story]
            for comp in (l_exp, l_h, l_metric):
                comp.change(board, [l_exp, l_h, l_metric], l_outs)
            app.load(board, [l_exp, l_h, l_metric], l_outs)

        with gr.Tab("Head to head"):
            names0 = [label(m) for m in models_of(exps[0])]
            with gr.Row():
                d_exp = gr.Radio(exps, value=exps[0], label="Experiment")
                d_a = gr.Dropdown(names0, value=label("timestral_209M"), label="Model A")
                d_b = gr.Dropdown(names0, value=label("lightgbm"), label="Model B")
            d_md = gr.Markdown(elem_classes="fa-explain")
            d_plot = gr.Plot(show_label=False)
            for comp in (d_exp, d_a, d_b):
                comp.change(duel, [d_exp, d_a, d_b], [d_plot, d_md])
            app.load(duel, [d_exp, d_a, d_b], [d_plot, d_md])

        with gr.Tab("Does it pay?"):
            gr.Markdown(
                "A flexible consumer moves **4 MWh a day** into the hours a model predicts are "
                "cheapest, then pays the real auction price. Wholesale cost only, not a household bill."
            )
            s_models = gr.CheckboxGroup(
                [label(m) for m in models_of("Power prices")],
                value=[label("chronos_2"), label("lightgbm"), label("seasonal_naive_24h")],
                label="Strategies",
            )
            s_story = gr.Markdown(elem_classes="fa-explain")
            s_plot = gr.Plot(show_label=False)
            s_table = gr.Dataframe(interactive=False)
            s_models.change(scheduling, s_models, [s_plot, s_table, s_story])
            app.load(scheduling, s_models, [s_plot, s_table, s_story])

        with gr.Tab("Method"):
            gr.Markdown(METHOD_MD)
            with gr.Accordion("Glossary", open=False):
                gr.Markdown(GLOSSARY_MD)
    return app


if __name__ == "__main__":
    style = {"theme": THEME, "css": CSS, "head": HEAD}
    if int(gr.__version__.split(".")[0]) >= 6:
        build_app().launch(**style, allowed_paths=[str(ROOT / "assets")])
    else:
        build_app(style).launch(allowed_paths=[str(ROOT / "assets")])
