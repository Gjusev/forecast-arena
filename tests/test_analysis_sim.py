"""Tests for event analysis and the electricity scheduling simulation."""

import numpy as np
import polars as pl
import pytest

from forecast_arena.evaluation.analysis import dm_vs_baseline, event_detection_metrics
from forecast_arena.evaluation.simulation import _cheapest, run_simulation, simulate_day


class TestSimulation:
    def test_cheapest_picks_lowest(self):
        actual = np.array([50.0, 10.0, 30.0, -5.0, 20.0])
        assert _cheapest(actual, 2) == [3, 1]  # -5 and 10

    def test_oracle_bounds(self):
        rng = np.random.default_rng(7)
        filler = 80.0 + rng.normal(size=18) * 5  # hours 6..23, expensive
        actual = np.concatenate([[100.0, 1.0, 50.0, 2.0, 60.0, 3.0], filler])
        pred = actual.copy()
        pred[6] = 4.0  # model wrongly believes hour 6 is cheap (actual ~80)
        costs = simulate_day(actual, pred, yesterday_prices=None)
        assert costs["oracle"] == pytest.approx(1 + 2 + 3 + 50)
        assert costs["model"] == pytest.approx(1 + 2 + 3 + actual[6])
        assert costs["model"] > costs["oracle"]
        assert costs["fixed_midday"] == pytest.approx(sum(actual[10:14]))

    def test_run_simulation_no_future_access(self):
        # The model schedule must depend only on predicted prices; realized
        # costs come from actuals. Construct: model predicts perfectly ->
        # equals oracle.
        rows = []
        for day in range(3):
            actual = np.array([10.0, 90.0, 20.0, 80.0, 30.0, 70.0] * 4)
            for i, v in enumerate(actual):
                rows.append(
                    {
                        "experiment": "electricity",
                        "tier": "t",
                        "model": "m",
                        "series_id": "day_ahead_price/DE-LU",
                        "origin_ts": f"2026-01-0{day+1}",
                        "h": i + 1,
                        "y_true": v,
                        "y_pred": v,  # perfect prediction
                        "q05": None, "q10": None, "q25": None,
                        "q75": None, "q90": None, "q95": None,
                    }
                )
        preds = pl.DataFrame(rows)
        sim = run_simulation(preds, "m")
        assert sim.height == 3
        assert (sim["regret_vs_oracle_eur"] == 0).all()
        assert (sim["savings_vs_fixed_eur"] > 0).all()  # cheapest 4h < midday 4h


class TestAnalysis:
    def _frame(self):
        rng = np.random.default_rng(0)
        rows = []
        for model, scale in [("good", 1.0), ("bad", 5.0), ("seasonal_naive_24h", 3.0)]:
            for o in range(60):
                for h in [1, 24]:
                    y = 100 + rng.normal(size=1)[0]
                    rows.append(
                        {
                            "experiment": "e", "tier": "t", "model": model,
                            "series_id": "avg_delay_min/X", "origin_ts": f"o{o}",
                            "h": h, "y_true": y, "y_pred": y + abs(rng.normal()) * scale,
                            "q05": None, "q10": None, "q25": None,
                            "q75": None, "q90": None, "q95": None,
                        }
                    )
        return pl.DataFrame(rows)

    def test_dm_detects_difference(self):
        dm = dm_vs_baseline(self._frame(), [1, 24], baseline="seasonal_naive_24h")
        good = dm.filter(pl.col("model") == "good")
        assert (good["dm_stat"] < 0).all()  # loses less than baseline
        assert (good["p_value"] < 0.05).all()

    def test_event_detection_negative_prices(self):
        df = self._frame().with_columns(
            pl.when(pl.int_range(pl.len()) % 7 == 0)
            .then(-10.0)
            .otherwise(50.0)
            .alias("y_true_val")
        )
        df = df.with_columns(
            pl.col("y_true").alias("y_true"),
        )
        # synthesize price-like series
        rows = []
        rng = np.random.default_rng(1)
        for model in ["a", "b"]:
            for i in range(200):
                y = -20.0 if i % 10 == 0 else 60.0
                p = y if model == "a" else 60.0  # 'a' perfect, 'b' never predicts neg
                rows.append(
                    {
                        "experiment": "e", "tier": "t", "model": model,
                        "series_id": "day_ahead_price/DE-LU", "origin_ts": f"o{i//24}",
                        "h": (i % 24) + 1, "y_true": y, "y_pred": p,
                        "q05": None, "q10": None, "q25": None,
                        "q75": None, "q90": None, "q95": None,
                    }
                )
        ev = event_detection_metrics(pl.DataFrame(rows), {}, [1])
        a = ev.filter(pl.col("model") == "a").to_dicts()[0]
        b = ev.filter(pl.col("model") == "b").to_dicts()[0]
        assert a["neg_recall"] == 1.0 and a["neg_precision"] == 1.0
        assert b["neg_recall"] == 0.0  # never predicts negative
