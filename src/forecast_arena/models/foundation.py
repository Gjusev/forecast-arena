"""Zero-shot time series foundation model adapters.

Heavy imports are lazy so CI and baselines run without torch installed.
All adapters convert to float32, impute nothing (NaN passes through where the
backend supports it), and expose native quantiles when the model produces them.
"""

from __future__ import annotations

import logging
from importlib.util import find_spec

import numpy as np

from forecast_arena.models.base import ForecastResult, Forecaster

log = logging.getLogger(__name__)


def _has(pkg: str) -> bool:
    return find_spec(pkg) is not None


class TimestralForecasterAdapter(Forecaster):
    """Mistral Timestral (5M/28M/123M/209M), zero-shot, 21 quantiles.

    pip install git+https://github.com/mistralai/timestral.git
    """

    family = "foundation"
    supports_quantiles = True

    def __init__(self, model_id: str = "mistralai/Timestral-209M", device: str = "cpu"):
        self.name = f"timestral_{model_id.split('-')[-1]}"
        self.model_id = model_id
        self.device = device
        self._model = None

    def _load(self):
        if self._model is None:
            if not _has("timestral"):
                raise ImportError("pip install git+https://github.com/mistralai/timestral.git")
            from timestral import TimestralForecaster

            log.info("loading %s on %s", self.model_id, self.device)
            self._model = TimestralForecaster.from_pretrained(self.model_id, device=self.device)
        return self._model

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        m = self._load()
        ctx = np.asarray(history, dtype=np.float32).reshape(1, 1, -1)
        out = m.forecast(ctx, prediction_length=horizon)
        to_np = lambda t: np.asarray(t.detach().cpu() if hasattr(t, "detach") else t, dtype=float)
        q = to_np(out.quantiles)[0, 0]  # (H, Q)
        levels = np.asarray(out.quantile_levels, dtype=float)
        median = to_np(out.median)[0, 0]
        return ForecastResult(median, q, levels)


class Chronos2Adapter(Forecaster):
    """Amazon Chronos-2 via the chronos-forecasting package (pip)."""

    family = "foundation"
    supports_quantiles = True

    def __init__(self, model_id: str = "amazon/chronos-2", device: str = "cpu"):
        self.name = "chronos_2"
        self.model_id = model_id
        self.device = device
        self._pipeline = None

    def _load(self):
        if self._pipeline is None:
            if not _has("chronos"):
                raise ImportError("pip install chronos-forecasting")
            import torch
            from chronos import BaseChronosPipeline

            log.info("loading %s on %s", self.model_id, self.device)
            self._pipeline = BaseChronosPipeline.from_pretrained(
                self.model_id,
                device_map=self.device,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
            )
        return self._pipeline

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        import torch

        p = self._load()
        levels = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
        out = p.predict_quantiles(
            torch.tensor(np.asarray(history, dtype=np.float32)).reshape(1, 1, -1),
            prediction_length=horizon,
            quantile_levels=levels,
        )
        if isinstance(out, tuple):
            q, mean = out  # (batch, H, Q), (batch, H)
            quantiles = np.asarray(q[0].numpy(), dtype=float).reshape(horizon, len(levels))
            point = np.asarray(mean[0].numpy(), dtype=float).reshape(horizon)
        else:  # object with attributes
            quantiles = np.asarray(out.quantiles, dtype=float)[0].reshape(horizon, -1)
            point = np.asarray(getattr(out, "mean", out.median), dtype=float)[0].reshape(horizon)
        return ForecastResult(point, quantiles, np.asarray(levels, dtype=float))


class TimesFMAdapter(Forecaster):
    """Google TimesFM 3.0 (timesfm3 API, pip timesfm[torch])."""

    family = "foundation"
    supports_quantiles = True

    def __init__(self, model_id: str = "google/timesfm-3.0-pytorch", device: str = "cpu"):
        self.name = "timesfm_3_0"
        self.model_id = model_id
        self.device = device
        self._model = None

    def _load(self):
        if self._model is None:
            if not _has("timesfm3"):
                raise ImportError("pip install 'timesfm[torch]'")
            from timesfm3 import TimesFM3Forecaster

            log.info("loading %s on %s", self.model_id, self.device)
            self._model = TimesFM3Forecaster.from_pretrained(self.model_id, device=self.device)
        return self._model

    def forecast(self, history, horizon, known_future=None, series_id: str = ""):
        m = self._load()
        out = m.predict(
            np.asarray(history, dtype=np.float32), horizon, return_quantiles=True
        )
        levels = np.asarray(list(m.model.quantiles), dtype=float)
        point = np.asarray(out.forecast, dtype=float)
        if out.quantiles is not None:
            q = np.asarray(out.quantiles, dtype=float)
            return ForecastResult(point, q, levels)
        return ForecastResult(point)
