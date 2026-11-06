"""Electricity scheduling simulation (ADR-0002 business layer).

A flexible consumer must place ENERGY_HOURS of consumption within one delivery
day's 24 hourly slots. Each strategy picks its slots using ONLY information it
is allowed to know; realized cost is always evaluated at ACTUAL prices.

Wholesale market costs only — explicitly NOT a household bill estimate.
"""

from __future__ import annotations

import numpy as np
import polars as pl

ENERGY_HOURS = 4  # MWh placed in the cheapest 4 slots


def _cheapest(prices: np.ndarray, k: int = ENERGY_HOURS) -> list[int]:
    return list(np.argsort(prices, kind="stable")[:k])


def _cost(actual: np.ndarray, slots: list[int]) -> float:
    return float(sum(actual[i] for i in slots))


def simulate_day(
    actual_prices: np.ndarray,
    predicted_prices: np.ndarray | None,
    yesterday_prices: np.ndarray | None,
) -> dict[str, float]:
    """One delivery day. Returns realized cost per strategy.

    Strategies:
      oracle         — pick on actual prices (upper bound of savings)
      model          — pick on the model's predicted prices
      fixed_midday   — hours 10..13 (typical inflexible daytime operation)
      yesterday_best — pick yesterday's cheapest 4 hours (simple baseline)
    """
    n = len(actual_prices)
    k = min(ENERGY_HOURS, n)
    res = {"oracle": _cost(actual_prices, _cheapest(actual_prices, k))}
    res["fixed_midday"] = _cost(actual_prices, list(range(10, 10 + k)))
    if predicted_prices is not None:
        res["model"] = _cost(actual_prices, _cheapest(predicted_prices, k))
    if yesterday_prices is not None and len(yesterday_prices) == n:
        res["yesterday_best"] = _cost(actual_prices, _cheapest(yesterday_prices, k))
    return res


def run_simulation(preds: pl.DataFrame, model: str) -> pl.DataFrame:
    """Run the scheduling simulation for one model across all origins.

    preds: long-format predictions for the electricity experiment.
    Returns per-origin costs + savings vs fixed_midday and regret vs oracle.
    """
    pdf = preds.to_pandas()
    g = pdf[pdf.model == model]
    rows = []
    by_origin = {o: gg.sort_values("h") for o, gg in g.groupby("origin_ts")}
    origins = sorted(by_origin)
    for i, o in enumerate(origins):
        gg = by_origin[o]
        actual = gg.y_true.to_numpy(float)
        pred = gg.y_pred.to_numpy(float)
        if len(actual) < ENERGY_HOURS or not np.isfinite(actual).all():
            continue
        # 'yesterday' = the previous origin's actual day (origin_step=24h)
        prev = origins[i - 1] if i > 0 else None
        yday = by_origin[prev].y_true.to_numpy(float) if prev else None
        costs = simulate_day(actual, pred, yday if yday is not None and len(yday) == len(actual) else None)
        base = costs["fixed_midday"]
        rows.append(
            {
                "origin_ts": o,
                "oracle_cost": costs["oracle"],
                "model_cost": costs.get("model", float("nan")),
                "fixed_midday_cost": base,
                "yesterday_best_cost": costs.get("yesterday_best", float("nan")),
                "savings_vs_fixed_eur": base - costs.get("model", float("nan")),
                "regret_vs_oracle_eur": costs.get("model", float("nan")) - costs["oracle"],
                "mean_actual_price": float(actual.mean()),
            }
        )
    return pl.DataFrame(rows)
