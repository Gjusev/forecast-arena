"""Rolling-origin evaluation protocol with structural leakage guards.

Panels are dicts of contiguous hourly float arrays (NaN = missing slot).
Origins are integer indices into those arrays; every model receives history
truncated at the origin, so no model can see beyond it by construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class PanelSpec:
    """Configuration of one benchmark panel."""

    series: dict[str, np.ndarray]  # series_id -> hourly values (may contain NaN)
    horizon: int
    origin_step: int  # spacing between rolling origins
    min_train: int  # minimum history length before the first origin
    eval_horizons: list[int] = field(default_factory=list)  # steps ahead to report
    event_thresholds: dict[str, float] = field(default_factory=dict)

    def origins(self) -> list[int]:
        last_valid = min(len(v) for v in self.series.values()) - self.horizon
        o = list(range(self.min_train, last_valid + 1, self.origin_step))
        return o


def truncate_at(history: np.ndarray, origin: int) -> np.ndarray:
    """History strictly before the origin slot."""
    return history[:origin]


def assert_no_lookahead(panel: PanelSpec, origin: int, pred_len: int) -> None:
    if origin + pred_len > max(len(v) for v in panel.series.values()) + 1:
        raise ValueError("forecast would extend past series end")
    if origin < panel.min_train:
        raise ValueError(f"origin {origin} < min_train {panel.min_train}")


def train_test_split(
    series: np.ndarray, split_index: int
) -> tuple[np.ndarray, np.ndarray]:
    """Chronological split: series[:split_index] train, series[split_index:] test."""
    return series[:split_index], series[split_index:]


def freeze_thresholds_on_train(
    series: dict[str, np.ndarray], split_index: int, quantile: float
) -> dict[str, float]:
    """Per-series event thresholds from TRAIN data only (pre-registration)."""
    out: dict[str, float] = {}
    for sid, s in series.items():
        tr = s[:split_index]
        v = tr[np.isfinite(tr)]
        out[sid] = float(np.quantile(v, quantile)) if len(v) else float("nan")
    return out
