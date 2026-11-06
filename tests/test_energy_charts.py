"""Unit tests: energy-charts renewables chunking + hourly aggregation. No network."""

from datetime import UTC, datetime

import numpy as np
import polars as pl
import pytest

from forecast_arena.data.energy_charts import (
    ZONE,
    _payload_to_hourly_long,
    _yearly_chunks,
    build_renewables_panel,
)


def _payload() -> dict:
    # 2019-01-01 00:00 UTC + k*900s; the 01:00 UTC hour is fully null (gap).
    secs = [1546300800 + i * 900 for i in range(8)]
    return {
        "unix_seconds": secs,
        "apis": {
            "wind_onshore": [100.0, 200.0, 300.0, 400.0, None, None, None, None],
            "wind_offshore": [10.0, 20.0, None, 40.0, None, None, None, None],
            "solar": [0.0, 0.0, 0.0, 0.0, None, None, None, None],
        },
    }


class TestYearlyChunks:
    def test_yearly_span(self):
        chunks = _yearly_chunks(
            datetime(2019, 1, 1, tzinfo=UTC),
            datetime(2026, 11, 6, tzinfo=UTC),
        )
        assert len(chunks) == 8
        assert chunks[0] == (1546300800, 1577836800)  # 2019-01-01 -> 2020-01-01 UTC
        assert chunks[-1][1] == int(datetime(2026, 11, 6, tzinfo=UTC).timestamp())
        for (_a, b), (c, _) in zip(chunks, chunks[1:], strict=False):  # contiguous
            assert b == c

    def test_mid_year_start(self):
        chunks = _yearly_chunks(
            datetime(2019, 6, 1, tzinfo=UTC),
            datetime(2021, 1, 1, tzinfo=UTC),
        )
        assert len(chunks) == 2
        assert chunks[0][0] == int(datetime(2019, 6, 1, tzinfo=UTC).timestamp())
        assert chunks[0][1] == 1577836800

    def test_single_short_chunk(self):
        chunks = _yearly_chunks(
            datetime(2019, 1, 1, tzinfo=UTC),
            datetime(2019, 6, 1, tzinfo=UTC),
        )
        assert len(chunks) == 1 and chunks[0][0] < chunks[0][1]


class TestHourlyAggregation:
    def test_hourly_mean_wind_total_null_gap(self):
        df = _payload_to_hourly_long(_payload())
        assert df.columns == ["timestamp", "value", "target", "zone"]
        want = {"wind_onshore", "wind_offshore", "solar", "wind_total"}
        assert set(df["target"]) == want
        assert set(df["zone"]) == {ZONE}
        assert str(df["timestamp"].dtype) == "Datetime(time_unit='us', time_zone='Europe/Berlin')"

        berlin = "Europe/Berlin"
        at = lambda s: pl.col("timestamp") == pl.lit(s).str.to_datetime(time_zone=berlin)  # noqa: E731
        h0 = df.filter(at("2019-01-01 01:00"))  # = 00:00 UTC hour, winter = CET+1
        got = dict(zip(h0["target"], h0["value"], strict=True))
        assert got["wind_onshore"] == pytest.approx(250.0)
        assert got["wind_offshore"] == pytest.approx((10 + 20 + 40) / 3)
        assert got["solar"] == 0.0
        # per-15-min sum then hourly mean: [110, 220, null, 440] -> 770/3
        assert got["wind_total"] == pytest.approx(770 / 3)

        # fully null hour survives as null rows (honest gap)
        h1 = df.filter(at("2019-01-01 02:00"))
        assert h1.height == 4 and h1["value"].null_count() == 4
        assert df.height == 8  # 2 hours x 4 targets


class TestPanel:
    def test_panel_filters_and_ids(self, tmp_path):
        cache = tmp_path / "renewables_hourly.parquet"
        _payload_to_hourly_long(_payload()).write_parquet(cache)
        grid, _, series = build_renewables_panel(cache, start="2019-01-01", end=None)
        want = sorted(
            f"{t}/{ZONE}" for t in ["wind_onshore", "wind_offshore", "solar", "wind_total"]
        )
        assert sorted(series) == want
        assert len(grid) == 2 and all(len(v) == len(grid) for v in series.values())
        assert series["wind_onshore/DE-LU"][0] == pytest.approx(250.0)
        assert np.isnan(series["wind_onshore/DE-LU"][1])

        # end exclusive
        _, _, s2 = build_renewables_panel(cache, start="2019-01-01", end="2019-01-01 02:00")
        assert len(s2["solar/DE-LU"]) == 1 and s2["solar/DE-LU"][0] == 0.0
        # start inclusive
        _, _, s3 = build_renewables_panel(cache, start="2019-01-01 02:00")
        assert len(s3["solar/DE-LU"]) == 1 and np.isnan(s3["solar/DE-LU"][0])


class TestWireShapes:
    def test_production_types_shape(self):
        p = _payload()
        live = {
            "unix_seconds": p["unix_seconds"],
            "production_types": [
                {"name": "Wind onshore", "data": p["apis"]["wind_onshore"]},
                {"name": "Wind offshore", "data": p["apis"]["wind_offshore"]},
                {"name": "Solar", "data": p["apis"]["solar"]},
                {"name": "Load", "data": [1.0] * len(p["unix_seconds"])},  # ignored
            ],
        }
        df = _payload_to_hourly_long(live)
        assert set(df["target"]) == {"wind_onshore", "wind_offshore", "solar", "wind_total"}
        h0 = df.filter(
            pl.col("timestamp")
            == pl.lit("2019-01-01 01:00").str.to_datetime(time_zone="Europe/Berlin")
        )
        got = dict(zip(h0["target"], h0["value"], strict=True))
        assert got["wind_onshore"] == pytest.approx(250.0)
        assert got["wind_total"] == pytest.approx(770 / 3)
