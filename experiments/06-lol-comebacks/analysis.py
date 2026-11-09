"""Comeback anticipation analysis for experiment 06 (standalone script).

Pre-registered (fixed before any forecast was computed): a match is
comeback-eligible when gold_diff at the origin (game-minute 15) is <= -2000
(blue behind by 2000+ gold). Reality flip: the actual gold_diff is >= 0 at any
game-minute 16..35. A model "predicts" the comeback when its point forecast
crosses 0 at any h <= 20. Reports precision / recall / F1 of that signal
against reality, plus the base rate any constant predictor would score.

Usage: uv run python experiments/06-lol-comebacks/analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

from forecast_arena.data.lol import ranked_match_ids

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
REPO = HERE.parents[1]
CACHE = REPO / "data" / "raw" / "lol" / "lol_gold_minute.parquet"
SUMMARY = REPO / "data" / "raw" / "lol" / "matches_summary.parquet"

THRESHOLD_AT_15 = -2000  # pre-registered: gold_diff <= -2000 at minute 15
FLIP_FROM, FLIP_TO = 16, 35  # inclusive game-minute window for the reality flip


def _load_predictions() -> tuple[pl.DataFrame, str]:
    path = RESULTS / "predictions.parquet"
    if not path.exists():
        sys.exit(f"no predictions at {path}; run `arena run 06` first")
    preds = pl.read_parquet(path)
    for tier in ("full", "pilot"):
        sub = preds.filter(pl.col("tier") == tier)
        if sub.height:
            return sub, tier
    sys.exit("predictions.parquet has no full/pilot rows; run a bigger tier first")


def _reality_from_cache() -> tuple[set[str], set[str]]:
    """(eligible match ids at minute 15, ids that actually flipped by minute 35)."""
    if not CACHE.exists():
        sys.exit(f"cache missing at {CACHE}; run `arena build-data 06` first")
    cache = pl.read_parquet(CACHE).with_columns(
        (pl.col("ts") - pl.datetime(2000, 1, 1)).dt.total_minutes().alias("minute")
    )
    keep = ranked_match_ids(SUMMARY.parent)
    if keep is not None:
        cache = cache.filter(pl.col("zone").is_in(keep))
    eligible = set(
        cache.filter((pl.col("minute") == 15) & (pl.col("value") <= THRESHOLD_AT_15))[
            "zone"
        ].to_list()
    )
    flipped = set(
        cache.filter(
            (pl.col("minute") >= FLIP_FROM) & (pl.col("minute") <= FLIP_TO) & (pl.col("value") >= 0)
        )["zone"].to_list()
    )
    return eligible, flipped


def _predicted_set(preds: pl.DataFrame, model: str, eligible: set[str]) -> set[str]:
    g = preds.filter((pl.col("model") == model) & (pl.col("y_pred") >= 0))
    return eligible & set(g["match_id"].to_list())


def main() -> None:
    preds, tier = _load_predictions()
    preds = preds.with_columns(pl.col("series_id").str.split("/").list.get(1).alias("match_id"))
    eligible, flipped = _reality_from_cache()
    panel = set(preds["match_id"].to_list())  # only matches this tier actually forecast
    eligible &= panel
    flipped &= eligible
    n_elig = len(eligible)
    n_flip = len(flipped)
    base_rate = n_flip / n_elig if n_elig else 0.0

    models: dict[str, dict] = {}
    for model in preds["model"].unique().to_list():
        predicted = _predicted_set(preds, model, eligible)
        tp = len(predicted & flipped)
        fp = len(predicted - flipped)
        fn = len(flipped - predicted)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        models[model] = {
            "predicted": len(predicted),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
        }

    patch_note = ""
    if SUMMARY.exists():
        s = pl.read_parquet(SUMMARY)
        if "match_id" in s.columns:
            s = s.filter(pl.col("match_id").is_in(panel))
        patch_counts = s.group_by("patch").len().sort("len", descending=True).head(1)
        if patch_counts.height and patch_counts["patch"][0] is not None:
            share = patch_counts["len"][0] / s.height if s.height else 0.0
            patch_note = (
                f" Most common patch among analysed matches: {patch_counts['patch'][0]} "
                f"({patch_counts['len'][0]} of {s.height}, {share:.0%})."
            )

    notes = [
        "ranked matches only (queues 420/440): ARAM and Arena gold curves are excluded as a "
        "different process",
        "matches from the same patch share meta; rows are correlated, not independent samples",
        "60 s frame resolution: leads that flip and re-flip inside a minute are invisible",
    ]
    report = {
        "tier": tier,
        "pre_registered": {
            "threshold_gold_diff_at_15": THRESHOLD_AT_15,
            "reality_flip": f"gold_diff >= 0 at any minute {FLIP_FROM}..{FLIP_TO}",
            "note": "constant fixed before any forecast was computed",
        },
        "eligible_matches": n_elig,
        "actually_flipped": n_flip,
        "base_rate": round(base_rate, 3),
        "models": models,
        "honesty_notes": notes,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report_assets_comebacks.json").write_text(json.dumps(report, indent=2))

    lines = [
        "# Comeback anticipation (experiment 06)",
        "",
        f"Tier: **{tier}**. Pre-registered rule: comeback-eligible = gold_diff at minute 15 "
        f"<= {THRESHOLD_AT_15} (blue behind by 2000+ gold). Reality flip = gold_diff >= 0 at "
        f"any game-minute {FLIP_FROM}..{FLIP_TO}. A model predicts a comeback when its point "
        "forecast crosses 0 at any h <= 20.",
        "",
        f"Of **{n_elig}** eligible matches, **{n_flip}** actually flipped "
        f"(base rate {base_rate:.1%}).{patch_note}",
        "",
        "| model | predicted | TP | FP | FN | precision | recall | F1 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for m, v in models.items():
        lines.append(
            f"| {m} | {v['predicted']} | {v['tp']} | {v['fp']} | {v['fn']} "
            f"| {v['precision']} | {v['recall']} | {v['f1']} |"
        )
    lines += [
        "",
        "In plain language: we keep only the matches where one side was clearly behind at "
        f"minute 15 (at least {abs(THRESHOLD_AT_15):,} gold down), and ask which models said - "
        "within their next-20-minute forecast - that the trailing side would pull level "
        "(forecast crossing 0). Precision is how often that call was right; recall is how "
        "many real turnarounds it caught. Because a share of matches flip anyway, a constant "
        f"'always comeback' call would score precision {base_rate:.3f} at recall 1.0, so a "
        "model only earns credit above that line.",
        "",
        "Honesty notes:",
        *[f"- {n}" for n in notes],
    ]
    md = "\n".join(lines) + "\n"
    (RESULTS / "report_assets_comebacks.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
