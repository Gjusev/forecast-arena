"""Collect PEGELONLINE (WSV) river gauge water levels into one local parquet.

The public REST API only serves a ~31-day history window per gauge, so this
must run regularly (daily is plenty) to accumulate history for a future
experiment. Output lands in data/raw/hydro/pegel_levels.parquet (gitignored);
this script is the reproducible entry point.

Usage:
    uv run python scripts/collect_pegelonline.py
    uv run python scripts/collect_pegelonline.py --stations KAUB,CELLE
    uv run python scripts/collect_pegelonline.py --full-backfill --max-stations 25
"""

import argparse
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import polars as pl

API = "https://www.pegelonline.wsv.de/webservices/rest-api/v2"
PARQUET = Path("data/raw/hydro/pegel_levels.parquet")
TZ = ZoneInfo("Europe/Berlin")
TARGET = "water_level"

SCHEMA = {
    "timestamp": pl.Datetime("us", "Europe/Berlin"),
    "value": pl.Float64,
    "zone": pl.String,
    "target": pl.String,
}


def empty() -> pl.DataFrame:
    return pl.DataFrame(schema=SCHEMA)


def fetch_json(url: str, timeout: float = 30.0):
    """GET a URL and parse JSON, retrying once on any network/HTTP error."""
    req = urllib.request.Request(url, headers={"User-Agent": "forecast-arena-collector/0.1"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == 2:
                raise
            time.sleep(1.0)


def parse_rows(rows: list[dict], zone: str) -> pl.DataFrame:
    """API measurement dicts -> frame with SCHEMA; drops rows without a value."""
    clean = [
        (datetime.fromisoformat(r["timestamp"]), float(r["value"]))
        for r in rows
        if r.get("value") is not None
    ]
    return pl.DataFrame(
        {
            "timestamp": [t for t, _ in clean],
            "value": [v for _, v in clean],
            "zone": [zone] * len(clean),
            "target": [TARGET] * len(clean),
        },
        schema=SCHEMA,
    )


def merge(existing: pl.DataFrame, new: pl.DataFrame) -> tuple[pl.DataFrame, int]:
    """Append only (timestamp, zone) rows we do not store yet.

    Returns (merged, rows_added). Existing rows win on collision, so running
    the collector twice in a row adds zero rows.
    """
    new = new.unique(subset=["timestamp", "zone"], keep="first", maintain_order=True)
    if existing.height == 0:
        return new.sort("zone", "timestamp"), new.height
    merged = (
        pl.concat([existing, new])
        .unique(subset=["timestamp", "zone"], keep="first", maintain_order=True)
        .sort("zone", "timestamp")
    )
    return merged, merged.height - existing.height


def latest_per_zone(df: pl.DataFrame) -> dict[str, datetime]:
    if df.height == 0:
        return {}
    return dict(df.group_by("zone").agg(pl.col("timestamp").max()).iter_rows())


def select_stations(stations_filter: str | None, max_stations: int | None) -> list[dict]:
    """Stations with a W timeseries, as {uuid, zone}."""
    stations = fetch_json(f"{API}/stations.json?{urlencode({'timeseries': 'W'})}")
    out = [{"uuid": s["uuid"], "zone": s["shortname"]} for s in stations]
    if stations_filter:
        wanted = {n.strip().upper() for n in stations_filter.split(",") if n.strip()}
        out = [s for s in out if s["zone"] in wanted]
    if max_stations:
        out = out[:max_stations]
    return out


def collect_station(
    station: dict, latest: dict[str, datetime], full_backfill: bool
) -> pl.DataFrame:
    """Fetch one gauge's measurements; tail-only if we already store history."""
    url = f"{API}/stations/{station['uuid']}/W/measurements.json"
    last = latest.get(station["zone"])
    if last is not None and not full_backfill:
        days = max(1, (datetime.now(TZ) - last).days + 1)
        url += "?" + urlencode({"start": f"P{days}D"})
    return parse_rows(fetch_json(url) or [], station["zone"])


def hf_sync(repo_id: str, merged: pl.DataFrame) -> int:
    """Sync month-partitioned parquet files to a Hugging Face dataset repo.

    Pulls every months/YYYY-MM.parquet from the repo, merges with the local
    frame, and re-uploads the partitioned files. Makes a CI run stateless:
    each run reconstructs the full history from HF plus the fresh API window.
    """
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi()
    api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
    remote = empty()
    pulled = 0
    try:
        for f in api.list_repo_files(repo_id, repo_type="dataset"):
            if f.startswith("months/") and f.endswith(".parquet"):
                p = Path(hf_hub_download(repo_id, f, repo_type="dataset"))
                remote = pl.concat([remote, pl.read_parquet(p)])
                pulled += 1
    except Exception as exc:  # noqa: BLE001 - first run has no files yet
        print(f"hf pull: {exc} (pulled {pulled} file(s))")
    combined, _ = merge(remote, merged)
    months_dir = PARQUET.parent / "months"
    months_dir.mkdir(parents=True, exist_ok=True)
    by_month = combined.with_columns(pl.col("timestamp").dt.strftime("%Y-%m").alias("month"))
    uploaded = 0
    for (month,), part in by_month.group_by("month"):
        f = months_dir / f"{month}.parquet"
        part.drop("month").write_parquet(f)
        api.upload_file(
            path_or_fileobj=f,
            path_in_repo=f"months/{month}.parquet",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"collect {month}",
        )
        uploaded += 1
    return uploaded


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stations", help="comma-separated station shortnames, e.g. KAUB,CELLE")
    ap.add_argument(
        "--full-backfill", action="store_true", help="refetch the full API window for all stations"
    )
    ap.add_argument("--max-stations", type=int, help="cap number of stations (quick tests)")
    ap.add_argument(
        "--hf-repo",
        help="dataset repo (e.g. Gjusev/pegelonline) to persist month parquet files to",
    )
    args = ap.parse_args(argv)

    t0 = time.monotonic()
    existing = pl.read_parquet(PARQUET) if PARQUET.exists() else empty()
    latest = latest_per_zone(existing)
    stations = select_stations(args.stations, args.max_stations)
    print(f"stations to fetch: {len(stations)} (stored zones so far: {len(latest)})")

    frames: list[pl.DataFrame] = []
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = []
        for i, station in enumerate(stations):
            futures.append(pool.submit(collect_station, station, latest, args.full_backfill))
            if i < len(stations) - 1:
                time.sleep(0.05)  # stagger submissions; 4 workers cap concurrency
        for station, fut in zip(stations, futures, strict=False):
            try:
                frames.append(fut.result())
            except Exception as exc:  # noqa: BLE001 - skip-and-log per station
                failures.append(f"{station['zone']}: {exc}")

    merged, rows_added = merge(existing, pl.concat(frames) if frames else empty())
    PARQUET.parent.mkdir(parents=True, exist_ok=True)
    merged.write_parquet(PARQUET)

    new_latest = merged["timestamp"].max()
    print(f"stations stored: {len(frames)}/{len(stations)}")
    if args.hf_repo:
        uploaded = hf_sync(args.hf_repo, merged)
        print(f"hf sync: {uploaded} month file(s) -> {args.hf_repo}")
    print(f"rows added: {rows_added}")
    print(f"total rows: {merged.height}")
    print(f"latest timestamp: {new_latest}")
    print(f"elapsed: {time.monotonic() - t0:.1f}s -> {PARQUET}")
    if failures:
        print(f"failed ({len(failures)}): " + "; ".join(failures))


if __name__ == "__main__":
    main()
