"""Unit tests for the PEGELONLINE collector (parse + merge/dedupe). No network."""

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import collect_pegelonline as cp

BERLIN = ZoneInfo("Europe/Berlin")


def mk(rows, zone="KAUB"):
    """Build a frame from (iso-timestamp, value) pairs as the API returns them."""
    return cp.parse_rows([{"timestamp": ts, "value": v} for ts, v in rows], zone)


def test_parse_rows_schema_and_tz():
    df = mk([("2026-11-06T17:45:00+01:00", 56.0), ("2026-11-06T17:30:00+01:00", 55.5)])
    assert df.schema == pl.Schema(cp.SCHEMA)
    assert df["timestamp"].dtype == pl.Datetime("us", "Europe/Berlin")
    assert df["value"].dtype == pl.Float64
    assert df["zone"].unique().to_list() == ["KAUB"]
    assert df["target"].unique().to_list() == ["water_level"]
    # UTC offset input is preserved as the same instant, expressed in Berlin
    assert df["timestamp"][0] == datetime(2026, 11, 6, 17, 45, tzinfo=BERLIN)


def test_parse_rows_converts_other_offsets_and_drops_nulls():
    df = mk(
        [
            ("2026-07-06T17:45:00+02:00", 100.0),  # summer = CEST
            ("2026-11-06T17:45:00+01:00", None),  # dropped
        ]
    )
    assert df.height == 1
    assert df["timestamp"][0] == datetime(2026, 7, 6, 17, 45, tzinfo=BERLIN)


def test_parse_rows_empty_measurements():
    df = cp.parse_rows([], "KAUB")
    assert df.height == 0
    assert df.schema == pl.Schema(cp.SCHEMA)


def test_merge_into_empty():
    new = mk([("2026-11-06T17:45:00+01:00", 56.0)])
    merged, added = cp.merge(cp.empty(), new)
    assert added == 1 and merged.height == 1


def test_merge_is_idempotent():
    new = mk([("2026-11-06T17:45:00+01:00", 56.0), ("2026-11-06T17:30:00+01:00", 55.5)])
    merged, added1 = cp.merge(cp.empty(), new)
    merged, added2 = cp.merge(merged, new)
    assert added1 == 2 and added2 == 0 and merged.height == 2


def test_merge_appends_only_newer_rows():
    existing = mk([("2026-11-05T10:00:00+01:00", 50.0), ("2026-11-05T10:15:00+01:00", 51.0)])
    fetched = mk(
        [
            ("2026-11-05T10:15:00+01:00", 51.0),  # overlap, refetched
            ("2026-11-05T10:30:00+01:00", 52.0),
            ("2026-11-05T10:45:00+01:00", 53.0),
        ]
    )
    merged, added = cp.merge(existing, fetched)
    assert added == 2
    assert merged.height == 4
    assert merged["timestamp"].is_sorted()


def test_merge_keeps_existing_value_on_collision():
    existing = mk([("2026-11-05T10:00:00+01:00", 50.0)])
    fetched = mk([("2026-11-05T10:00:00+01:00", 99.0)])
    merged, added = cp.merge(existing, fetched)
    assert added == 0
    assert merged["value"][0] == 50.0


def test_merge_keeps_zones_separate():
    a = mk([("2026-11-05T10:00:00+01:00", 50.0)], zone="KAUB")
    b = mk([("2026-11-05T10:00:00+01:00", 20.0)], zone="CELLE")
    merged, added = cp.merge(cp.merge(cp.empty(), a)[0], b)
    assert added == 1 and merged.height == 2
    assert sorted(merged["zone"].to_list()) == ["CELLE", "KAUB"]


def test_merge_dedupes_within_one_fetch():
    fetched = pl.concat(
        [mk([("2026-11-05T10:00:00+01:00", 50.0)]), mk([("2026-11-05T10:00:00+01:00", 51.0)])]
    )
    merged, added = cp.merge(cp.empty(), fetched)
    assert added == 1 and merged.height == 1


def test_latest_per_zone():
    df = pl.concat(
        [
            mk([("2026-11-05T10:00:00+01:00", 50.0), ("2026-11-05T11:00:00+01:00", 52.0)], "KAUB"),
            mk([("2026-11-05T09:00:00+01:00", 20.0)], "CELLE"),
        ]
    )
    latest = cp.latest_per_zone(df)
    assert latest["KAUB"] == datetime(2026, 11, 5, 11, 0, tzinfo=BERLIN)
    assert latest["CELLE"] == datetime(2026, 11, 5, 9, 0, tzinfo=BERLIN)
    assert cp.latest_per_zone(cp.empty()) == {}
