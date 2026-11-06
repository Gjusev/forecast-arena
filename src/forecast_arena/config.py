"""YAML experiment configuration with defaults and validation."""

from __future__ import annotations

from pathlib import Path

import yaml

DEFAULTS = {
    "protocol": {
        "horizon": 24,
        "eval_horizons": [1, 3, 6, 24],
        "origin_step_hours": 168,
        "min_train_hours": 2160,  # 90 days
    },
    "tiers": {
        "smoke": {"n_origins": 2, "series_limit": 1},
        "pilot": {"n_origins": 8, "series_limit": None},
        "full": {"n_origins": None, "series_limit": None},
    },
}


def load_config(path: Path) -> dict:
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    merged = dict(DEFAULTS)
    for k, v in (cfg or {}).items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v
    if "experiment" not in merged:
        raise ValueError(f"{path}: 'experiment' key required")
    return merged


def tier_settings(cfg: dict, tier: str) -> dict:
    tiers = cfg.get("tiers", {})
    if tier not in tiers:
        raise ValueError(f"unknown tier {tier!r}; have {list(tiers)}")
    base = dict(DEFAULTS["tiers"].get(tier, {}))
    base.update(tiers[tier])
    return base
