"""Live check: all foundation adapters produce conforming forecasts.

Downloads model weights on first run. Skipped unless ARENA_LIVE_TESTS=1
(CI never sets it).
"""

import os

import numpy as np
import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("ARENA_LIVE_TESTS") != "1", reason="live test; set ARENA_LIVE_TESTS=1"
)

from forecast_arena.models.base import ForecastResult  # noqa: E402
from forecast_arena.models.foundation import (  # noqa: E402
    Chronos2Adapter,
    TimesFMAdapter,
    TimestralForecasterAdapter,
)


def test_foundation_adapters_forecast():
    rng = np.random.default_rng(0)
    history = np.cumsum(rng.normal(0, 1, 400)).astype(np.float32) + 50.0

    for adapter in [
        TimestralForecasterAdapter("mistralai/Timestral-28M"),
        Chronos2Adapter(),
        TimesFMAdapter(),
    ]:
        res = adapter.forecast(history, 24)
        assert isinstance(res, ForecastResult)
        assert res.point.shape == (24,), res.point.shape
        assert np.isfinite(res.point).all(), "point forecast has non-finite values"
        if res.quantiles is not None:
            assert res.quantiles.shape[0] == 24
            assert res.quantiles.shape[1] == len(res.quantile_levels)
            # monotonicity of quantiles per step
            assert np.all(np.diff(res.quantiles, axis=1) >= -1e-4), "quantiles cross"
