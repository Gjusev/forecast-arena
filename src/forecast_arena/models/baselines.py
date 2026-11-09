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


class Persistence(Forecaster):
    """The next H steps stay where the series is now: y[t+h] = y[t].

    For gold curves inside a single match this is the honest "the gap holds"
    baseline every forecast must beat.
    """

    def __init__(self, name: str = "persistence"):
        self.name = name

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        hist = np.asarray(history, dtype=float)
        last = hist[-1] if np.isfinite(hist[-1]) else np.nanmean(hist)
        point = np.full(horizon, float(last))
        finite = hist[np.isfinite(hist)]
        if len(finite) >= 5:
            spread = float(np.std(np.diff(finite))) * np.sqrt(np.arange(1, horizon + 1))
            qlevels = np.array([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
            quantiles = (
                point[:, None]
                + spread[:, None]
                * np.array([-1.645, -1.282, -0.674, 0, 0.674, 1.282, 1.645])[None, :]
            )
            return ForecastResult(point, quantiles, qlevels)
        return ForecastResult(point)


class Drift(Forecaster):
    """Extrapolate the recent slope, damped: y[t+h] = y[t] + h * slope / (1 + 0.1*h).

    Damping keeps long horizons from flying away on a noisy local trend.
    """

    def __init__(self, window: int = 5, name: str = "drift"):
        self.window = window
        self.name = name

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        hist = np.asarray(history, dtype=float)
        tail = hist[-self.window - 1 :]
        slope = float(np.polyfit(np.arange(len(tail)), tail, 1)[0])
        h = np.arange(1, horizon + 1)
        damp = 1.0 / (1.0 + 0.1 * (h - 1))
        point = hist[-1] + h * slope * damp
        finite = hist[np.isfinite(hist)]
        if len(finite) >= 5:
            resid = finite[1:] - finite[:-1]
            spread = float(np.std(resid)) * np.sqrt(h)
            qlevels = np.array([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
            quantiles = (
                point[:, None]
                + spread[:, None]
                * np.array([-1.645, -1.282, -0.674, 0, 0.674, 1.282, 1.645])[None, :]
            )
            return ForecastResult(np.asarray(point, dtype=float), quantiles, qlevels)
        return ForecastResult(np.asarray(point, dtype=float))
