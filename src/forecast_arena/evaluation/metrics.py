"""Forecast metrics. Vectorised NumPy; NaN-aware where emptiness is genuine."""

from __future__ import annotations

import math

import numpy as np


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    m = np.isfinite(y_true) & np.isfinite(y_pred)
    if not m.any():
        return float("nan")
    return float(np.mean(np.abs(y_true[m] - y_pred[m])))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    m = np.isfinite(y_true) & np.isfinite(y_pred)
    if not m.any():
        return float("nan")
    return float(np.sqrt(np.mean((y_true[m] - y_pred[m]) ** 2)))


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    m = np.isfinite(y_true) & np.isfinite(y_pred)
    if not m.any():
        return float("nan")
    yt, yp = y_true[m], y_pred[m]
    denom = np.abs(yt) + np.abs(yp)
    ok = denom > 0
    return float(100 * np.mean(2 * np.abs(yt[ok] - yp[ok]) / denom[ok]))


def seasonal_mae(y_true: np.ndarray, season: int = 24) -> float:
    """In-sample--free seasonal-naive errors: |y[t] - y[t-season]| on the eval set."""
    m = np.isfinite(y_true)
    if m.sum() <= season:
        return float("nan")
    yt = y_true[m]
    return float(np.mean(np.abs(yt[season:] - yt[:-season])))


def mase(y_true: np.ndarray, y_pred: np.ndarray, baseline_mae: float) -> float:
    """MAE of the forecast divided by the (pre-registered) seasonal-naive MAE."""
    if not np.isfinite(baseline_mae) or baseline_mae == 0:
        return float("nan")
    return mae(y_true, y_pred) / baseline_mae


def interval_coverage(
    y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray
) -> float:
    m = np.isfinite(y_true) & np.isfinite(lower) & np.isfinite(upper)
    if not m.any():
        return float("nan")
    return float(np.mean((y_true[m] >= lower[m]) & (y_true[m] <= upper[m])))


def diebold_mariano(
    e1: np.ndarray, e2: np.ndarray, loss: str = "ae", h: int = 1
) -> tuple[float, float]:
    """DM test that mean loss difference != 0. Returns (statistic, p_value).

    Uses heteroskedasticity/autocorrelation-consistent (HAC) variance with
    Newey-West lag = h. e1/e2 are aligned forecast errors (same slots).
    """
    m = np.isfinite(e1) & np.isfinite(e2)
    e1, e2 = e1[m], e2[m]
    if len(e1) < 30:
        return float("nan"), float("nan")
    l1 = np.abs(e1) if loss == "ae" else e1**2
    l2 = np.abs(e2) if loss == "ae" else e2**2
    d = l1 - l2
    n = len(d)
    dbar = d.mean()
    dc = d - dbar
    lag = min(h, n // 5)
    gamma0 = np.mean(dc**2)
    var = gamma0
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1)
        var += 2 * w * np.mean(dc[l:] * dc[:-l])
    if var <= 0:
        return float("nan"), float("nan")
    stat = dbar / np.sqrt(var / n)
    p = math.erfc(abs(stat) / math.sqrt(2))  # two-sided normal p-value
    return float(stat), float(p)


def event_detection(
    y_true: np.ndarray, y_pred: np.ndarray, threshold: float
) -> dict[str, float]:
    """Precision/recall/F1 for binary event = value >= threshold.

    For negative events callers pass a negated series and threshold 0
    (i.e. event = -value >= 0).
    """
    m = np.isfinite(y_true) & np.isfinite(y_pred)
    yt, yp = y_true[m] >= threshold, y_pred[m] >= threshold
    tp = int(np.sum(yt & yp))
    fp = int(np.sum(~yt & yp))
    fn = int(np.sum(yt & ~yp))
    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if tp else float("nan")
    return {
        "n_events": int(np.sum(yt)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }
