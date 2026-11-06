"""Panel construction for both experiments.

A panel is dict[series_id -> contiguous hourly float array] plus the timestamp
grid it sits on. Grid = sorted union of observed timestamps (so DST days have
their true 23/25 wall-clock slots). Series IDs follow
'<group>/<station|zone>/<target>' conventions per experiment.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl


def grid_and_series(
    df: pl.DataFrame,
    ts_col: str,
    group_cols: list[str],
    value_col: str,
) -> tuple[list, np.ndarray, dict[str, np.ndarray]]:
    """Union timestamp grid + DST-correct hour-of-week + aligned arrays.

    Hour-of-week is computed in the timestamps' own time zone (Europe/Berlin
    wall clock), so DST days map correctly. NaN marks absent slots.
    """
    grid_df = df.select(ts_col).unique().sort(ts_col)
    grid = grid_df[ts_col].to_list()
    how = (
        grid_df.with_columns(
            (pl.col(ts_col).dt.weekday().cast(pl.Int32) - 1).alias("dow")  # Monday=0
        )
        .with_columns((pl.col("dow") * 24 + pl.col(ts_col).dt.hour().cast(pl.Int32)).alias("how"))[
            "how"
        ]
        .to_numpy()
        .astype(np.int64)
    )
    pos = {t: i for i, t in enumerate(grid)}
    n = len(grid)
    out: dict[str, np.ndarray] = {}
    for key, g in df.group_by(group_cols, maintain_order=True):
        sid = "/".join(str(k) for k in (key if isinstance(key, tuple) else (key,)))
        arr = np.full(n, np.nan)
        for t, v in zip(g[ts_col].to_list(), g[value_col].to_list(), strict=False):
            arr[pos[t]] = v if v is not None else np.nan
        out[sid] = arr
    return grid, how, out


def build_train_delays_panel(
    agg_path: Path,
    stations: list[str],
    targets: list[str],
    start: str | None = None,
    end: str | None = None,
) -> tuple[list, np.ndarray, dict[str, np.ndarray]]:
    df = pl.read_parquet(agg_path)
    df = df.filter(pl.col("station").is_in(stations))
    if start:
        df = df.filter(pl.col("hour_start") >= pl.lit(start).str.to_datetime())
    if end:
        df = df.filter(pl.col("hour_start") < pl.lit(end).str.to_datetime())
    # long: station x target series
    long_frames = []
    for target in targets:
        long_frames.append(
            df.select(
                "hour_start",
                "station",
                pl.lit(target).alias("target"),
                pl.col(target).cast(pl.Float64).alias("value"),
            )
        )
    long = pl.concat(long_frames)
    return grid_and_series(long, "hour_start", ["target", "station"], "value")


def build_electricity_panel(
    price_path: Path,
    start: str | None = None,
    end: str | None = None,
) -> tuple[list, np.ndarray, dict[str, np.ndarray]]:
    """DE day-ahead prices as one series 'day_ahead_price/DE-LU'."""
    df = pl.read_parquet(price_path).with_columns(pl.col("value").alias("price"))
    tz = "Europe/Berlin"
    if start:
        lo = pl.lit(start).str.to_datetime(time_zone=tz)
        df = df.filter(pl.col("timestamp") >= lo)
    if end:
        hi = pl.lit(end).str.to_datetime(time_zone=tz)
        df = df.filter(pl.col("timestamp") < hi)
    df = df.with_columns(pl.lit("DE-LU").alias("zone"), pl.lit("day_ahead_price").alias("target"))
    return grid_and_series(df, "timestamp", ["target", "zone"], "price")
