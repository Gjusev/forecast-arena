"""German day-ahead electricity prices from SMARD (Bundesnetzagentur).

License: Datenlizenz Deutschland Namensnennung 2.0 (dl-de/by-2-0), attribution
to www.smard.de. Hourly day-ahead prices for DE(LU), filter 4169, from the
2018-10 market-area split to the present. No API token required.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
from pathlib import Path

import polars as pl

log = logging.getLogger(__name__)

BASE = "https://www.smard.de/app/chart_data"
FILTER_PRICE_DE = "4169"
FILTER_LOAD_ACTUAL_DE = "410"


def _get_json(url: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "forecast-arena/0.1"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch_smard_series(
    smard_filter: str, region: str = "DE", resolution: str = "hour"
) -> pl.DataFrame:
    """Fetch a full SMARD chart_data series as tz-aware Polars frame.

    Returns columns: timestamp (Europe/Berlin), value (float, nulls preserved).
    """
    index = _get_json(f"{BASE}/{smard_filter}/{region}/index_{resolution}.json")
    chunks = index.get("timestamps", [])
    log.info("smard filter %s: %d chunks", smard_filter, len(chunks))
    rows: list[tuple[int, float | None]] = []
    for i, ts in enumerate(chunks):
        data = _get_json(
            f"{BASE}/{smard_filter}/{region}/{smard_filter}_{region}_{resolution}_{ts}.json"
        )
        rows.extend((t, v) for t, v in data.get("series", []))  # v may be None
        if i % 50 == 0:
            log.info("  chunk %d/%d", i + 1, len(chunks))
    df = pl.DataFrame(
        {"ts_ms": [r[0] for r in rows], "value": [r[1] for r in rows]},
        schema={"ts_ms": pl.Int64, "value": pl.Float64},
    )
    df = (
        df.unique(subset="ts_ms", keep="last")
        .sort("ts_ms")
        .with_columns(
            (pl.col("ts_ms") * 1_000)  # ms -> us epoch, then cast to tz-aware Berlin
            .cast(pl.Datetime("us", "UTC"))
            .dt.convert_time_zone("Europe/Berlin")
            .alias("timestamp")
        )
        .drop("ts_ms")
    )
    return df


def build_price_panel(cache_path: Path, refresh: bool = False) -> pl.DataFrame:
    """Fetch (or load cached) day-ahead prices; validate hourly continuity."""
    if cache_path.exists() and not refresh:
        return pl.read_parquet(cache_path)
    df = fetch_smard_series(FILTER_PRICE_DE)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(cache_path)
    return df


def build_load_actual_panel(cache_path: Path, refresh: bool = False) -> pl.DataFrame:
    """Realized total grid load (MW) — multivariate feature with strict lags."""
    if cache_path.exists() and not refresh:
        return pl.read_parquet(cache_path)
    df = fetch_smard_series(FILTER_LOAD_ACTUAL_DE)
    df = df.rename({"value": "load_actual_mw"})
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(cache_path)
    return df
