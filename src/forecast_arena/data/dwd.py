"""DWD CDC hourly 2m air temperature for 30 German city stations.

License: CC BY 4.0 (DWD Open Data Nutzungsbedingungen, www.dwd.de/DE/service/copyright),
attribution: Deutscher Wetterdienst (DWD), https://opendata.dwd.de/climate_environment/CDC/.
Hourly TU product: per station the historical archive zip plus the rolling recent zip,
so the cache runs to the last published hour. TT_TU is 2m air temperature in degrees
Celsius (-999 = missing -> null). Timestamps are station local time (Europe/Berlin).
DWD repeats the fall-back hour in legal time, so the two 02:00 rows collapse to one
instant (ambiguous="earliest", deduped); the non-existent spring-forward 02:00 row
becomes null and is dropped.
"""

from __future__ import annotations

import io
import logging
import re
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import polars as pl

log = logging.getLogger(__name__)

BASE = (
    "https://opendata.dwd.de/climate_environment/CDC/observations_germany"
    "/climate/hourly/air_temperature"
)
MISSING = -999.0
TARGET = "air_temperature"

# Station id -> city label. 30 active stations, one per major German city, all
# 16 federal states covered, longest available records (full table with record
# start and state in experiments/03-dwd-weather/README.md).
STATIONS: dict[str, str] = {
    "00433": "Berlin-Tempelhof",
    "01975": "Hamburg-Fuhlsbuettel",
    "01262": "Muenchen-Flughafen",
    "02667": "Koeln-Bonn",
    "01420": "Frankfurt-Main",
    "04928": "Stuttgart-Schnarrenberg",
    "01078": "Duesseldorf",
    "02928": "Leipzig-Holzhausen",
    "01048": "Dresden-Klotzsche",
    "00691": "Bremen",
    "02014": "Hannover",
    "03668": "Nuernberg",
    "01303": "Essen-Bredeney",
    "00662": "Braunschweig",
    "05906": "Mannheim",
    "01443": "Freiburg",
    "01270": "Erfurt-Weimar",
    "04271": "Rostock-Warnemuende",
    "03987": "Potsdam",
    "03126": "Magdeburg",
    "04336": "Saarbruecken-Ensheim",
    "05100": "Trier-Petrisberg",
    "03137": "Mainz-Lerchenberg",
    "02564": "Kiel-Holtenau",
    "04625": "Schwerin",
    "00880": "Cottbus",
    "04104": "Regensburg",
    "05705": "Wuerzburg",
    "01684": "Goerlitz",
    "02712": "Konstanz",
}

# produkt files: header STATIONS_ID;MESS_DATUM;QN_9;TT_TU;RF_TU;eor, fields
# space-padded, -999 = missing, MESS_DATUM = YYYYMMDDHH local time.
SCHEMA = {
    "STATIONS_ID": pl.Utf8,
    "MESS_DATUM": pl.Utf8,
    "QN_9": pl.Utf8,
    "TT_TU": pl.Float64,
    "RF_TU": pl.Utf8,
    "eor": pl.Utf8,
}


def _download(url: str, dest: Path, retries: int = 3) -> None:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "forecast-arena/0.1"})
            with urllib.request.urlopen(req, timeout=180) as r:
                dest.write_bytes(r.read())
            return
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def _listing(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "forecast-arena/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("latin-1")


def _hist_zip_names() -> dict[str, str]:
    """Map station id -> its dated '<von>_<bis>_hist.zip' (dates vary per station)."""
    pat = r'href="(stundenwerte_TU_(\d{5})_\d{8}_\d{8}_hist\.zip)"'
    pairs = re.findall(pat, _listing(f"{BASE}/historical/"))
    out = {sid: name for name, sid in pairs}
    missing = set(STATIONS) - set(out)
    if missing:
        raise FileNotFoundError(f"no historical zip for stations {sorted(missing)}")
    return out


def _station_frame(zip_path: Path) -> pl.DataFrame:
    """Parse all produkt_tu_stunde_* members (one per measurement period)."""
    parts: list[pl.DataFrame] = []
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if "produkt_tu_stunde" not in name:
                continue
            parts.append(
                pl.read_csv(io.BytesIO(z.read(name)), separator=";", schema_overrides=SCHEMA)
            )
    if not parts:
        raise ValueError(f"{zip_path}: no produkt_tu_stunde file")
    return pl.concat(parts, how="vertical_relaxed")


def _to_long(df: pl.DataFrame, sid: str) -> pl.DataFrame:
    """Produkt rows -> long cache rows: timestamp (Berlin), value, target, zone."""
    return (
        df.with_columns(
            pl.concat_str([pl.col("MESS_DATUM"), pl.lit("00")])
            .str.to_datetime(format="%Y%m%d%H%M", strict=False)
            .dt.replace_time_zone("Europe/Berlin", ambiguous="earliest", non_existent="null")
            .alias("timestamp"),
            pl.when(pl.col("TT_TU") == MISSING)
            .then(None)
            .otherwise(pl.col("TT_TU"))
            .alias("value"),
        )
        .drop_nulls("timestamp")
        .with_columns(pl.lit(TARGET).alias("target"), pl.lit(sid).alias("zone"))
        .select("timestamp", "value", "target", "zone")
    )


def refresh_raw(raw_dir: Path) -> Path:
    """Download historical + recent zips for all stations; write the hourly cache."""
    raw_dir = Path(raw_dir)
    tmp = raw_dir / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    hist_names = _hist_zip_names()
    frames: list[pl.DataFrame] = []
    for i, sid in enumerate(sorted(STATIONS), start=1):
        hist_zip = tmp / f"tu_{sid}_hist.zip"
        if not hist_zip.exists():
            _download(f"{BASE}/historical/{hist_names[sid]}", hist_zip)
        hist = _to_long(_station_frame(hist_zip), sid)
        akt_zip = tmp / f"tu_{sid}_akt.zip"
        if not akt_zip.exists():
            _download(f"{BASE}/recent/stundenwerte_TU_{sid}_akt.zip", akt_zip)
        akt = _to_long(_station_frame(akt_zip), sid)
        # recent overwrites the archive tail (any post-revision rows win)
        station = pl.concat([hist, akt]).sort("timestamp")
        station = station.unique(subset=["timestamp", "zone"], keep="last")
        frames.append(station)
        log.info(
            "station %s (%d/%d): %d rows %s -> %s",
            sid,
            i,
            len(STATIONS),
            station.height,
            station["timestamp"].min(),
            station["timestamp"].max(),
        )
    cache = raw_dir / "dwd_weather_hourly.parquet"
    df = pl.concat(frames).sort("timestamp", "zone")
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(cache)
    log.info(
        "dwd cache: %d rows, %d stations, %s -> %s",
        df.height,
        df["zone"].n_unique(),
        df["timestamp"].min(),
        df["timestamp"].max(),
    )
    return cache


def build_dwd_panel(
    hourly_path: Path,
    start: str | None = None,
    end: str | None = None,
) -> tuple[list, np.ndarray, dict[str, np.ndarray]]:
    """Long cache -> panel via grid_and_series; ids like 'air_temperature/00433'."""
    from forecast_arena.data.panels import grid_and_series

    df = pl.read_parquet(hourly_path)
    tz = "Europe/Berlin"
    if start:
        df = df.filter(pl.col("timestamp") >= pl.lit(start).str.to_datetime(time_zone=tz))
    if end:
        df = df.filter(pl.col("timestamp") < pl.lit(end).str.to_datetime(time_zone=tz))
    return grid_and_series(df, "timestamp", ["target", "zone"], "value")
