"""Statistical baselines: the bar every foundation model must clear."""

from __future__ import annotations

import numpy as np

from forecast_arena.models.base import Forecaster, ForecastResult


class SeasonalNaive(Forecaster):
    """Repeat the last `season` observations: y[t+H] = y[t+H-season].

    For hourly data season=24 repeats yesterday; at 10:00 D-1 this uses D-1's
    published day-ahead prices — exactly the strongest honest day-ahead baseline.
    """

    def __init__(self, season: int = 24, name: str = "seasonal_naive_24h"):
        self.season = season
        self.name = name

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        hist = np.asarray(history, dtype=float)
        tail = hist[-self.season :]
        reps = int(np.ceil(horizon / self.season))
        point = np.tile(tail, reps)[:horizon]
        # Empirical residual spread over the last 14 days → 80%/90% intervals.
        if len(hist) >= self.season * 15:
            fitted = np.tile(hist[-self.season * 14 : -self.season * 14 + self.season], 14)[
                : self.season * 14
            ]
            resid = hist[-self.season * 14 :] - fitted
            qlevels = np.array([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
            rq = np.quantile(resid, qlevels)
            quantiles = point[:, None] + rq[None, :]
            return ForecastResult(point, quantiles, qlevels)
        return ForecastResult(point)


class HourOfWeekClimatology(Forecaster):
    """Average by (day-of-week, hour) over the history. Slow-moving, honest."""

    def __init__(self, name: str = "hour_of_week_climatology"):
        self.name = name

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        hist = np.asarray(history, dtype=float)
        n = len(hist)
        if known_future is not None and "hour_of_week" in known_future.columns:
            how_target = known_future.values[:, known_future.columns.index("hour_of_week")].astype(
                int
            )
            # Last history slot sits one step before target step 1.
            hist_end_how = int(how_target[0]) - 1
            idx = (hist_end_how - np.arange(n)) % 168
            sums = np.bincount(idx, weights=np.nan_to_num(hist), minlength=168)
            counts = np.bincount(idx, minlength=168).astype(float)
            means = np.divide(sums, counts, out=np.zeros(168), where=counts > 0)
            finite = np.isfinite(hist)
            global_mean = float(hist[finite].mean()) if finite.any() else 0.0
            means[counts == 0] = global_mean
            point = means[how_target % 168]
        else:
            hour = np.arange(n) % 24
            sums = np.bincount(hour, weights=np.nan_to_num(hist), minlength=24)
            counts = np.bincount(hour, minlength=24).astype(float)
            means = np.divide(sums, counts, out=np.zeros(24), where=counts > 0)
            point = np.tile(means, int(np.ceil(horizon / 24)))[:horizon]
        return ForecastResult(np.asarray(point, dtype=float))
