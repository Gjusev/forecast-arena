"""Fast unit tests: metrics, protocol guards, baselines, GBMs. No downloads."""

import numpy as np
import polars as pl
import pytest

from forecast_arena.evaluation import metrics as M
from forecast_arena.evaluation.protocol import (
    PanelSpec,
    assert_no_lookahead,
    freeze_thresholds_on_train,
    truncate_at,
)
from forecast_arena.models.base import KnownFuture
from forecast_arena.models.baselines import HourOfWeekClimatology, SeasonalNaive
from forecast_arena.models.gbms import LightGBMModel, build_training_matrix


def _daily_cycle(n: int, noise: float = 0.0, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    return 10 + 5 * np.sin(2 * np.pi * t / 24) + noise * rng.normal(size=n)


class TestMetrics:
    def test_mae_rmse_basic(self):
        y = np.array([1.0, 2.0, 3.0, 4.0])
        p = np.array([1.5, 2.0, 2.0, 5.0])
        assert M.mae(y, p) == pytest.approx((0.5 + 0 + 1 + 1) / 4)
        assert M.rmse(y, p) == pytest.approx(np.sqrt((0.25 + 0 + 1 + 1) / 4))

    def test_nan_ignored(self):
        y = np.array([1.0, np.nan, 3.0])
        p = np.array([1.0, 99.0, 2.0])
        assert M.mae(y, p) == pytest.approx(0.5)

    def test_smape_zero_safe(self):
        y = np.array([0.0, 100.0])
        p = np.array([0.0, 50.0])
        v = M.smape(y, p)
        assert np.isfinite(v)

    def test_mase(self):
        y = np.arange(10, dtype=float)
        assert M.mase(y, y, baseline_mae=2.0) == 0.0
        assert M.mase(y, y + 1, baseline_mae=1.0) == 1.0

    def test_coverage(self):
        y = np.array([0.0, 10.0])
        assert M.interval_coverage(y, np.array([-1.0, 9.0]), np.array([1.0, 11.0])) == 1.0
        assert M.interval_coverage(y, np.array([1.0, 11.0]), np.array([2.0, 12.0])) == 0.0

    def test_dm_test_perfect_forecast(self):
        rng = np.random.default_rng(1)
        rng.normal(size=500)
        e1 = np.zeros(500)  # perfect
        e2 = np.abs(rng.normal(size=500))  # competitor errors
        stat, p = M.diebold_mariano(e1, e2)
        assert stat < 0  # e1 loses less
        assert p < 0.01

    def test_event_detection(self):
        y = np.array([1.0, 5.0, 1.0, 1.0])
        p = np.array([5.0, 5.0, 1.0, 5.0])
        det = M.event_detection(y, p, threshold=3.0)
        assert det["n_events"] == 1
        assert det["precision"] == pytest.approx(1 / 3)
        assert det["recall"] == 1.0


class TestProtocol:
    def test_truncate_at(self):
        s = np.arange(100.0)
        assert truncate_at(s, 10).shape == (10,)
        assert truncate_at(s, 10)[-1] == 9

    def test_no_lookahead_guard(self):
        spec = PanelSpec(series={"a": np.zeros(100)}, horizon=24, origin_step=10, min_train=30)
        with pytest.raises(ValueError):
            assert_no_lookahead(spec, origin=20, pred_len=24)  # below min_train

    def test_origins_step(self):
        spec = PanelSpec(series={"a": np.zeros(200)}, horizon=24, origin_step=50, min_train=30)
        o = spec.origins()
        assert o[0] == 30 and 80 in o and o[-1] <= 176

    def test_threshold_frozen_on_train_only(self):
        rng = np.random.default_rng(0)
        s = {"x": rng.uniform(size=1000)}
        thr = freeze_thresholds_on_train(s, split_index=500, quantile=0.9)
        expected = float(np.quantile(s["x"][:500], 0.9))
        assert thr["x"] == pytest.approx(expected)


class TestPanels:
    def test_hour_of_week_no_int8_overflow(self):
        # Regression: polars dt.weekday() is Int8; dow*24 overflows for Sundays
        # unless cast. Sunday 22:00 must be 166, not -90.
        from forecast_arena.data.panels import grid_and_series

        df = pl.DataFrame(
            {
                "ts": ["2024-06-30 22:00", "2024-07-01 00:00", "2024-07-01 05:00"],
                "g": ["a", "a", "a"],
                "v": [1.0, 2.0, 3.0],
            }
        ).with_columns(pl.col("ts").str.to_datetime())
        _, how, series = grid_and_series(df, "ts", ["g"], "v")
        assert how.tolist() == [166, 0, 5]
        assert series["a"].tolist() == [1.0, 2.0, 3.0]


class TestBaselines:
    def test_seasonal_naive_repeats_yesterday(self):
        h = _daily_cycle(240)
        pred = SeasonalNaive(24).forecast(h, 24)
        np.testing.assert_allclose(pred.point, h[-24:])

    def test_climatology_smooth(self):
        h = _daily_cycle(24 * 30)
        pred = HourOfWeekClimatology().forecast(h, 24)
        assert pred.point.shape == (24,)
        assert abs(pred.point.mean() - h.mean()) < 1.0


class TestGBM:
    def test_training_matrix_no_future_leakage(self):
        # With a pure AR(1) process y[t] = 0.9*y[t-1] + eps, features at t must
        # only involve indices < t by construction of _row_values.
        rng = np.random.default_rng(0)
        y = np.zeros(600)
        for t in range(1, 600):
            y[t] = 0.9 * y[t - 1] + rng.normal(0, 0.1)
        how = np.arange(600) % 168
        X, target = build_training_matrix({"s": y}, {"s": 0}, how)
        assert X.shape[0] == target.shape[0]
        assert X.shape[0] == 600 - 337
        # lag-1 feature must equal target shifted by one
        lag1_col = 3  # after 3 calendar cols, first lag is lag-1
        np.testing.assert_allclose(X[1:, lag1_col], target[:-1], rtol=1e-5)

    def test_lightgbm_predicts_sine(self):
        h = _daily_cycle(24 * 40, noise=0.1, seed=3)
        m = LightGBMModel(n_estimators=80)
        m.set_calendar(np.arange(len(h)) % 168)
        cut = len(h) - 24
        m.prepare({"s": h[:cut]}, cut)
        vals = (np.arange(cut, cut + 24) % 168).reshape(-1, 1)
        known = KnownFuture(columns=["hour_of_week"], values=vals)
        pred = m.forecast(h[:cut], 24, known_future=known, series_id="s")
        # next day of the same sine: should beat a 2.0 MAE bar
        truth = h[-24:]
        assert M.mae(truth, pred.point) < 2.0
