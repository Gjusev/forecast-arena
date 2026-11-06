"""Model registry and experiment orchestration (config -> panel -> benchmark)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import polars as pl

from forecast_arena.config import load_config, tier_settings
from forecast_arena.data.panels import build_electricity_panel, build_train_delays_panel
from forecast_arena.evaluation.protocol import PanelSpec, freeze_thresholds_on_train
from forecast_arena.evaluation.runner import run_benchmark, summarize
from forecast_arena.models.base import Forecaster
from forecast_arena.models.baselines import HourOfWeekClimatology, SeasonalNaive
from forecast_arena.models.foundation import (
    Chronos2Adapter,
    TimesFMAdapter,
    TimestralForecasterAdapter,
)
from forecast_arena.models.gbms import LightGBMModel, XGBoostModel
from forecast_arena.utils import provenance

log = logging.getLogger(__name__)


def _timestral(size: str):
    return lambda: TimestralForecasterAdapter(f"mistralai/Timestral-{size}")


REGISTRY: dict[str, object] = {
    "seasonal_naive_24h": SeasonalNaive,
    "hour_of_week_climatology": HourOfWeekClimatology,
    "lightgbm": LightGBMModel,
    "xgboost": XGBoostModel,
    "timestral_28m": _timestral("28M"),
    "timestral_209m": _timestral("209M"),
    "chronos_2": Chronos2Adapter,
    "timesfm_3_0": TimesFMAdapter,
}


def build_models(names: list[str]) -> list[Forecaster]:
    models: list[Forecaster] = []
    for n in names:
        if n not in REGISTRY:
            raise ValueError(f"unknown model {n!r}; have {sorted(REGISTRY)}")
        obj = REGISTRY[n]
        models.append(obj() if callable(obj) else obj)  # type: ignore[operator]
    return models


def _panel_for(cfg: dict) -> tuple[list, np.ndarray, dict[str, np.ndarray]]:
    exp = cfg["experiment"]
    data = cfg.get("data", {})
    if exp == "train-delays":
        return build_train_delays_panel(
            Path(data["aggregates"]),
            stations=cfg["stations"],
            targets=cfg.get("targets", ["avg_delay_min", "n_delayed_gt5"]),
            start=data.get("start"),
            end=data.get("end"),
        )
    if exp == "electricity":
        return build_electricity_panel(
            Path(data["prices"]), start=data.get("start"), end=data.get("end")
        )
    raise ValueError(f"unknown experiment {exp!r}")


def run_experiment(config_path: Path, tier: str, models_override: list[str] | None = None) -> Path:
    cfg = load_config(config_path)
    ts = tier_settings(cfg, tier)
    grid, grid_how, series = _panel_for(cfg)

    # Tier slicing (deterministic): first K sorted series, last K origins.
    if ts.get("series_limit"):
        ids = sorted(series)[: int(ts["series_limit"])]
        series = {k: series[k] for k in ids}

    proto = cfg.get("protocol", {})
    horizon = int(proto.get("horizon", 24))
    spec = PanelSpec(
        series=series,
        horizon=horizon,
        origin_step=int(proto.get("origin_step_hours", 168)),
        min_train=int(proto.get("min_train_hours", 2160)),
        eval_horizons=list(proto.get("eval_horizons", [1, 3, 6, 24])),
    )
    origins = spec.origins()
    if ts.get("n_origins"):
        spec.min_train = origins[-int(ts["n_origins"]) :][0]

    thresholds: dict[str, float] = {}
    if cfg.get("events"):
        q = float(cfg["events"].get("train_quantile", 0.9))
        thresholds = freeze_thresholds_on_train(series, spec.min_train, q)

    model_names = models_override or ts.get("models") or cfg.get("models", ["seasonal_naive_24h"])
    models = build_models(model_names)
    out_dir = Path(cfg.get("results_dir", config_path.parent / "results"))
    origin_dt = {o: str(grid[o]) for o in spec.origins()}

    provenance.write_provenance(out_dir, cfg["experiment"], tier, cfg)
    preds = run_benchmark(
        cfg["experiment"],
        tier,
        spec,
        models,
        out_dir,
        origin_datetimes=origin_dt,
        grid_how=grid_how,
    )
    preds = preds.filter(pl.col("tier") == tier)
    baseline = cfg.get("baseline_model", "seasonal_naive_24h")
    summary = summarize(
        preds,
        spec.eval_horizons,
        baseline_model=baseline,
        event_thresholds=thresholds,
    )
    summary.write_parquet(out_dir / f"metrics_{tier}.parquet")
    (out_dir / f"metrics_{tier}.json").write_text(
        json.dumps({"thresholds": thresholds, "baseline": baseline}, indent=2)
    )
    log.info("metrics -> %s (thresholds: %s)", out_dir, thresholds)
    return out_dir / f"metrics_{tier}.parquet"
