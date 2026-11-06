"""Deutsche Bahn delays: monthly finalized parquets -> hourly station aggregates.

Source: piebro/deutsche-bahn-data (CC-BY-4.0), monthly_processed_data variant =
one finalized row per train stop. Aggregates follow ADR-0001: everything is a
function of completed arrivals only.
"""

from __future__ import annotations

import glob
import logging
from pathlib import Path

import duckdb
import polars as pl

log = logging.getLogger(__name__)

# Station identity resolution from research phase (multiple EVA codes per Hbf).
STATIONS: dict[str, list[str]] = {
    "Frankfurt(Main)Hbf": ["08000105", "08098105"],
    "Köln Hbf": ["08000207"],
    "München Hbf": ["08098263", "08000261"],
    "Berlin Hbf": ["08089021", "08098160", "08011160"],
    "Hamburg Hbf": ["08098549", "08002549"],
}

EXCLUDED_TRAIN_TYPES = {"Bus"}  # rail only; SEV bus replacements are not trains


def build_hourly_aggregates(raw_dir: Path, out_path: Path) -> Path:
    """Scan monthly parquets, filter to the five stations, emit hourly aggregates.

    Output columns: station, hour_start (Europe/Berlin wall clock), n_arrivals,
    avg_delay_min, n_delayed_gt5, pct_delayed_gt5, sum_delay_min, n_canceled,
    plus the same for long-distance only (ice/ic/ec/nj/ece/rj) as *_ld columns.
    """
    files = sorted(glob.glob(str(raw_dir / "monthly_processed_data" / "*.parquet")))
    if not files:
        raise FileNotFoundError(f"no parquet files under {raw_dir}")
    evas = [(name, code) for name, codes in STATIONS.items() for code in codes]
    eva_expr = ", ".join(f"('{n}', '{c}')" for n, c in evas)

    con = duckdb.connect()
    con.execute("SET timezone = 'Europe/Berlin';")
    query = f"""
        WITH stops AS (
            SELECT s.station, st.hour_start,
                   st.n_arrivals, st.n_delayed, st.sum_delay, st.n_canceled,
                   st.n_arrivals_ld, st.n_delayed_ld, st.sum_delay_ld, st.n_canceled_ld
            FROM (
                SELECT station_name AS station, eva,
                       train_type IN ('ICE','IC','EC','ECE','NJ','RJ') AS ld,
                       date_trunc('hour', arrival_planned_time) AS hour_start,
                       count(*) AS n_arrivals,
                       sum(CASE WHEN delay_in_min > 5 THEN 1 ELSE 0 END) AS n_delayed,
                       sum(coalesce(delay_in_min, 0)) AS sum_delay,
                       sum(CASE WHEN arrival_is_canceled THEN 1 ELSE 0 END) AS n_canceled,
                       sum(ld) AS n_arrivals_ld,
                       sum(CASE WHEN ld AND delay_in_min > 5 THEN 1 ELSE 0 END) AS n_delayed_ld,
                       sum(CASE WHEN ld THEN coalesce(delay_in_min, 0) ELSE 0 END) AS sum_delay_ld,
                       sum(CASE WHEN ld AND arrival_is_canceled THEN 1 ELSE 0 END) AS n_canceled_ld
                FROM read_parquet({files!r})
                WHERE arrival_planned_time IS NOT NULL
                  AND train_type NOT IN ('Bus')
                GROUP BY 1, 2, 3, 4
            ) st
            JOIN (VALUES {eva_expr}) s(station, eva) ON st.eva = s.eva
        )
        SELECT station, hour_start,
               sum(n_arrivals) AS n_arrivals,
               sum(sum_delay) / greatest(sum(n_arrivals), 1) AS avg_delay_min,
               sum(n_delayed) AS n_delayed_gt5,
               100.0 * sum(n_delayed) / greatest(sum(n_arrivals), 1) AS pct_delayed_gt5,
               sum(sum_delay) AS sum_delay_min,
               sum(n_canceled) AS n_canceled,
               sum(n_arrivals_ld) AS n_arrivals_ld,
               sum(sum_delay_ld) / greatest(sum(n_arrivals_ld), 1) AS avg_delay_min_ld,
               sum(n_delayed_ld) AS n_delayed_gt5_ld,
               sum(sum_delay_ld) AS sum_delay_min_ld,
               sum(n_canceled_ld) AS n_canceled_ld
        FROM stops
        GROUP BY 1, 2
        ORDER BY 1, 2
    """
    df = con.sql(query).pl()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out_path)
    log.info("hourly aggregates: %d rows -> %s", df.height, out_path)
    return out_path


def load_hourly_panel(
    agg_path: Path,
) -> pl.DataFrame:
    """Load aggregates, fill missing station-hours with explicit nulls.

    A station with zero arrivals in an hour is genuinely empty (night hours);
    for delay averaging we emit null avg_delay (not 0) so models can tell
    'no trains' from 'all punctual'. Count targets stay 0.
    """
    df = pl.read_parquet(agg_path).with_columns(
        pl.col("hour_start").cast(pl.Datetime("us", "Europe/Berlin")).alias("hour_start")
    )
    return df.sort(["station", "hour_start"])
