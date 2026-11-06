"""Common forecasting interface for all arena models.

Every model — foundation, gradient-boosted, or statistical baseline — is
ultimately a function from a value history to a fixed-horizon forecast.
Quantiles are optional; point forecasts are mandatory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np


@dataclass
class ForecastResult:
    """Forecast for one series at one origin.

    point: (H,) point forecast (median where quantiles exist).
    quantiles: optional (H, Q) forecasts at quantile_levels.
    """

    point: np.ndarray
    quantiles: np.ndarray | None = None
    quantile_levels: np.ndarray | None = None

    def __post_init__(self) -> None:
        if self.quantiles is not None and self.quantile_levels is None:
            raise ValueError("quantile_levels required when quantiles are given")
        self.point = np.asarray(self.point, dtype=float)

    def quantile(self, level: float) -> np.ndarray:
        i = int(np.argmin(np.abs(self.quantile_levels - level)))
        return self.quantiles[:, i]


@dataclass
class KnownFuture:
    """Covariates whose future values are known at the forecast origin.

    Hour-of-day, day-of-week, month etc. are always derivable; anything else
    (e.g. published day-ahead prices of not-yet-delivered hours) must be passed
    explicitly so models cannot invent it.
    """

    columns: list[str] = field(default_factory=list)
    values: np.ndarray | None = None  # (H, n_cols)


class Forecaster(ABC):
    """One model in the arena.

    `prepare` is called once per forecast origin (no-op for zero-shot models,
    retraining for fitted models — always on data available at that origin).
    `forecast` is then called per series. Implementations must never look at
    values after the origin: the runner only passes history up to it.
    """

    name: str = "forecaster"
    family: str = "baseline"  # 'foundation' | 'ml' | 'baseline'
    supports_quantiles: bool = False

    def prepare(self, histories: dict[str, np.ndarray], origin_index: int) -> None:
        """Optional per-origin preparation (fit). Histories end at the origin."""

    @abstractmethod
    def forecast(
        self,
        history: np.ndarray,
        horizon: int,
        known_future: KnownFuture | None = None,
        series_id: str = "",
    ) -> ForecastResult:
        """Forecast the next `horizon` steps after `history`.

        series_id identifies which panel series the history belongs to (used by
        global models like the GBMs; ignored by per-series forecasters).
        """
