"""Gradient-boosted tabular models with strictly lagged features.

One global model per origin over all series in the panel (transfer across
stations/days), trained only on target values at or before the origin.
Features: TRUE calendar (hour/day-of-week from grid timestamps, DST-correct),
lags + rolling stats. Recursive multi-step prediction (model feeds on its own
predictions beyond step 1).
"""

from __future__ import annotations

import numpy as np

from forecast_arena.models.base import ForecastResult, Forecaster

LAGS = [1, 2, 3, 24, 48, 72, 168, 336]
WINDOWS = [24, 168]
MIN_TRAIN = 337  # longest lag + 1 so every training row has all features


def _row_values(h: np.ndarray, t: int, sid: float, how_t: int) -> list[float]:
    """Feature values for slot t, using only h[:t]. how_t = slot's hour-of-week."""
    feats = [float(how_t % 24), float(how_t // 24), float(how_t)]
    feats += [float(h[t - lag]) for lag in LAGS]
    for w in WINDOWS:
        m = float(h[t - w : t].mean())
        feats += [m, float(h[t - 1]) - m]
    feats.append(sid)
    return feats


def build_training_matrix(
    histories: dict[str, np.ndarray],
    series_index: dict[str, int],
    how: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """(X, y) over all (series, t) with t >= MIN_TRAIN. y[t] uses only h[:t]."""
    X_rows, y_rows = [], []
    for sid, hist in histories.items():
        h = np.asarray(hist, dtype=float)
        if len(h) < MIN_TRAIN:
            continue
        si = float(series_index[sid])
        t = np.arange(MIN_TRAIN, len(h))
        rows = np.empty((len(t), 3 + len(LAGS) + 2 * len(WINDOWS) + 1), dtype=np.float32)
        for i, ti in enumerate(t):
            rows[i] = _row_values(h, int(ti), si, int(how[ti]))
        X_rows.append(rows)
        y_rows.append(h[MIN_TRAIN:])
    if not X_rows:
        raise ValueError("no series long enough for tabular training")
    X = np.vstack(X_rows)
    y = np.concatenate(y_rows)
    ok = np.isfinite(X).all(axis=1) & np.isfinite(y)
    return X[ok], y[ok]


class _GBMBase(Forecaster):
    family = "ml"
    refit_every = 7  # refit every N origins (expanding window between refits)

    def __init__(self, name: str, **params):
        self.name = name
        self.params = params
        self._model = None
        self._series_index: dict[str, int] = {}
        self._how: np.ndarray | None = None

    def _fit(self, X, y) -> None:  # pragma: no cover - overridden
        raise NotImplementedError

    def _predict(self, X) -> np.ndarray:  # pragma: no cover - overridden
        raise NotImplementedError

    def set_calendar(self, hour_of_week: np.ndarray) -> None:
        """DST-correct hour-of-week per grid slot (from the panel builder)."""
        self._how = np.asarray(hour_of_week, dtype=np.int64)

    def prepare(self, histories: dict[str, np.ndarray], origin_index: int) -> None:
        if self._how is None:
            raise RuntimeError("set_calendar() must run before prepare()")
        self._series_index = {sid: i for i, sid in enumerate(sorted(histories))}
        X, y = build_training_matrix(histories, self._series_index, self._how)
        self._fit(X, y)

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        if self._model is None:
            raise RuntimeError("prepare() must run before forecast()")
        sid = float(self._series_index.get(series_id, 0))
        buf = list(np.asarray(history, dtype=float))
        preds = np.empty(horizon, dtype=float)
        for step in range(horizon):
            t = len(buf)
            if known_future is not None and "hour_of_week" in known_future.columns:
                # Authoritative: the target slot's own calendar entry.
                how_t = int(
                    known_future.values[step, known_future.columns.index("hour_of_week")]
                )
            elif t < len(self._how):
                # Fallback: valid only when history was not truncated.
                how_t = int(self._how[t])
            else:  # pragma: no cover - runner always supplies calendar
                how_t = t % 168
            feats = _row_values(np.asarray(buf), t, sid, how_t)
            p = float(self._predict(np.asarray([feats], dtype=np.float32))[0])
            preds[step] = p
            buf.append(p)
        return ForecastResult(preds)


class LightGBMModel(_GBMBase):
    def __init__(self, name: str = "lightgbm", **params):
        super().__init__(name, **params)
        self.params = {"n_estimators": 500, "learning_rate": 0.05, "verbose": -1, **params}

    def _fit(self, X, y):
        import lightgbm as lgb

        self._model = lgb.LGBMRegressor(**self.params)
        self._model.fit(X, y)

    def _predict(self, X):
        return self._model.predict(X)


class XGBoostModel(_GBMBase):
    def __init__(self, name: str = "xgboost", **params):
        super().__init__(name, **params)
        self.params = {"n_estimators": 500, "learning_rate": 0.05, "max_depth": 6, **params}

    def _fit(self, X, y):
        import xgboost as xgb

        self._model = xgb.XGBRegressor(**self.params)
        self._model.fit(X, y)

    def _predict(self, X):
        return self._model.predict(X)
