"""German renewable generation from the Fraunhofer ISE energy-charts API.

License: CC BY 4.0 (attribution string is part of every API payload; see
experiments/04-renewables/README.md). Source: api.energy-charts.info
/public_power — 15-minute net generation (MW) per bidding zone. Zone change
DE-AT-LU -> DE-LU happened 2018-10, so we start 2019-01-01 to stay clean.

Raw fetch -> hourly mean (MW) -> one long parquet cache with targets
wind_onshore / wind_offshore / solar / wind_total (onshore + offshore summed
at 15-min level). energy-charts revises recent 15-min values, so a snapshot
is frozen at refresh time and scored as-is.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import polars as pl

log = logging.getLogger(__name__)

BASE = "https://api.energy-charts.info/public_power"
ZONE = "DE-LU"
DATA_START = datetime(2019, 1, 1, tzinfo=UTC)
API_TARGETS = ("wind_onshore", "wind_offshore", "solar")
TARGETS = API_TARGETS + ("wind_total",)  # wind_total is derived on fetch


def _get_json(url: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "forecast-arena/0.1"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def _yearly_chunks(start: datetime, end: datetime) -> list[tuple[int, int]]:
    """(unix_start, unix_end) pairs covering [start, end) in calendar years."""
    out: list[tuple[int, int]] = []
    cur = start
    while cur < end:
        nxt = datetime(cur.year + 1, 1, 1, tzinfo=UTC)
        stop = min(nxt, end)
        out.append((int(cur.timestamp()), int(stop.timestamp())))
        cur = nxt
    return out


def _normalize_apis(payload: dict) -> dict:
    """Accept both wire shapes of public_power.

    Legacy: {"apis": {"wind_onshore": [...]}}; live API: {"production_types":
    [{"name": "Wind onshore", "data": [...]}, ...]}. Returns snake_case keys.
    """
    if "apis" in payload:
        return {str(k).lower(): v for k, v in payload["apis"].items()}
    out: dict[str, list] = {}
    for p in payload.get("production_types", []):
        out[str(p.get("name", "")).lower().replace(" ", "_")] = p.get("data")
    return out


def _payload_to_hourly_long(payload: dict, zone: str = ZONE) -> pl.DataFrame:
    """One public_power payload -> hourly-mean long frame.

    Columns: timestamp (Europe/Berlin, tz-aware), value (float MW), target,
    zone. Hours are floored in UTC (whole-hour offset zone), so DST
    fall-back keeps its two distinct 02:00 instants. Nulls survive: an hour
    with only some 15-min values present takes the mean of those; a fully
    missing hour stays null.
    """
    apis = _normalize_apis(payload)
    missing = [t for t in API_TARGETS if t not in apis]
    if missing:
        raise ValueError(f"public_power payload missing series {missing}")
    schema = {"unix_seconds": pl.Int64, **{t: pl.Float64 for t in API_TARGETS}}
    wide = pl.DataFrame(
        {"unix_seconds": payload["unix_seconds"], **{t: apis[t] for t in API_TARGETS}},
        schema=schema,
    ).with_columns((pl.col("wind_onshore") + pl.col("wind_offshore")).alias("wind_total"))
    long = wide.unpivot(
        index="unix_seconds", on=list(TARGETS), value_name="value", variable_name="target"
    )
    return (
        long.with_columns(
            (pl.col("unix_seconds") * 1_000_000)
            .cast(pl.Datetime("us", "UTC"))
            .dt.truncate("1h")
            .alias("utc_hour")
        )
        .group_by("utc_hour", "target")
        .agg(pl.col("value").mean())
        .with_columns(
            pl.col("utc_hour").dt.convert_time_zone("Europe/Berlin").alias("timestamp"),
            pl.lit(zone).alias("zone"),
        )
        .select("timestamp", "value", "target", "zone")
        .sort("timestamp", "target")
    )


def refresh_raw(raw_dir: Path) -> Path:
    """Fetch 2019-01-01 -> now in yearly chunks; write the hourly cache."""
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache = raw_dir / "renewables_hourly.parquet"
    end = datetime.now(UTC)
    chunks = _yearly_chunks(DATA_START, end)
    frames: list[pl.DataFrame] = []
    for i, (s, e) in enumerate(chunks):
        payload = _get_json(f"{BASE}?bzn={ZONE}&start={s}&end={e}")
        frames.append(_payload_to_hourly_long(payload))
        log.info("chunk %d/%d (%s..%s) done", i + 1, len(chunks), s, e)
    df = pl.concat(frames).unique(subset=["timestamp", "target"], keep="last")
    df.write_parquet(cache)
    log.info(
        "renewables cache: %d rows %s -> %s",
        df.height,
        df["timestamp"].min(),
        df["timestamp"].max(),
    )
    return cache


def build_renewables_panel(
    hourly_path: Path,
    start: str | None = None,
    end: str | None = None,
) -> tuple[list, np.ndarray, dict[str, np.ndarray]]:
    """Long cache -> panel via grid_and_series; ids like 'wind_total/DE-LU'."""
    df = pl.read_parquet(hourly_path)
    tz = "Europe/Berlin"
    if start:
        df = df.filter(pl.col("timestamp") >= pl.lit(start).str.to_datetime(time_zone=tz))
    if end:
        df = df.filter(pl.col("timestamp") < pl.lit(end).str.to_datetime(time_zone=tz))
    from forecast_arena.data.panels import grid_and_series

    return grid_and_series(df, "timestamp", ["target", "zone"], "value")
