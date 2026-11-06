"""Run provenance: versions, config snapshot, result checksums."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path


def versions() -> dict[str, str]:
    out: dict[str, str] = {"python": sys.version.split()[0], "platform": platform.platform()}
    for pkg in ("numpy", "pandas", "polars", "pyarrow", "duckdb", "torch", "lightgbm", "xgboost"):
        try:
            mod = __import__(pkg)
            out[pkg] = getattr(mod, "__version__", "?")
        except ImportError:
            out[pkg] = "not-installed"
    return out


def write_provenance(out_dir: Path, experiment: str, tier: str, config: dict) -> Path:
    doc = {
        "experiment": experiment,
        "tier": tier,
        "versions": versions(),
        "config": config,
    }
    p = out_dir / f"provenance_{tier}.json"
    p.write_text(json.dumps(doc, indent=2, default=str))
    return p


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
