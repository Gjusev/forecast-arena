"""Fast unit tests for the DWD CDC parser. No downloads.

The inline produkt sample mirrors the real file: semicolon separated,
space-padded fields, trailing eor column, -999 = missing, MESS_DATUM =
YYYYMMDDHH local (Europe/Berlin) time.
"""

import io
import zipfile

import numpy as np
import polars as pl
import pytest

from forecast_arena.data.dwd import (
    MISSING,
    TARGET,
    _station_frame,
    _to_long,
    build_dwd_panel,
)


def _produkt_text(rows: list[str]) -> io.BytesIO:
    header = "STATIONS_ID;MESS_DATUM;QN_9;TT_TU;RF_TU;eor"
    return io.BytesIO(("\n".join([header, *rows]) + "\n").encode("ascii"))


def _row(sid: str, ts: str, tt: str) -> str:
    return f"{sid.rjust(10)};{ts};    1;{tt.rjust(6)};  88.0;eor"


def _produkt_df(rows: list[str]) -> pl.DataFrame:
    return pl.read_csv(
        _produkt_text(rows),
        separator=";",
        schema_overrides={
            "STATIONS_ID": pl.Utf8,
            "MESS_DATUM": pl.Utf8,
            "QN_9": pl.Utf8,
            "TT_TU": pl.Float64,
            "RF_TU": pl.Utf8,
            "eor": pl.Utf8,
        },
    )


class TestToLong:
    def test_parse_and_units(self):
        rows = [
            _row("00433", "2024030100", "5.1"),
            _row("00433", "2024030101", "4.8"),
            _row("00433", "2024030102", "-3.5"),
        ]
        out = _to_long(_produkt_df(rows), "00433")
        assert out.columns == ["timestamp", "value", "target", "zone"]
        assert out["zone"].unique().to_list() == ["00433"]  # zero-padded str
        assert out["target"].unique().to_list() == [TARGET]
        assert str(out["timestamp"].dtype) == "Datetime(time_unit='us', time_zone='Europe/Berlin')"
        vals = out.sort("timestamp")["value"].to_list()
        assert vals == [5.1, 4.8, -3.5]  # degrees Celsius, no /10 scaling

    def test_missing_to_null(self):
        rows = [
            _row("00433", "2024030100", "5.1"),
            _row("00433", "2024030101", "-999"),
            _row("00433", "2024030102", "-999"),
        ]
        out = _to_long(_produkt_df(rows), "00433")
        assert out["value"].to_list() == [5.1, None, None]
        assert out["value"].null_count() == 2

    def test_dst_fall_back_dedup_and_spring_forward_drop(self):
        # Fall-back night 2024-10-27: DWD lists 02:00 twice (CEST + CET) ->
        # both rows collapse to one instant, later row wins.
        rows = [
            _row("00433", "2024102702", "9.0"),
            _row("00433", "2024102702", "8.0"),
            _row("00433", "2024102703", "7.5"),
        ]
        long = _to_long(_produkt_df(rows), "00433")
        assert long["timestamp"].n_unique() == 2  # 02:00 collapses, 03:00 distinct

        # Spring-forward 2024-03-31: the 02:00 row does not exist locally ->
        # non_existent="null" -> dropped, not surfaced as a null timestamp.
        rows = [
            _row("00433", "2024033101", "6.0"),
            _row("00433", "2024033102", "6.5"),  # nonexistent local hour
            _row("00433", "2024033103", "7.0"),
        ]
        long = _to_long(_produkt_df(rows), "00433")
        assert long.height == 2
        assert long["timestamp"].null_count() == 0

    def test_quoted_separator_integrity(self):
        rows = [_row("00433", "2024030100", "-0.5")]
        out = _to_long(_produkt_df(rows), "00433")
        assert out["value"][0] == pytest.approx(-0.5)


class TestStationFrame:
    def test_reads_produkt_from_zip_multi_period(self, tmp_path):
        zpath = tmp_path / "hist.zip"
        with zipfile.ZipFile(zpath, "w") as z:
            z.writestr("Metadaten_Geographie_00433.txt", "junk metadata")
            z.writestr(
                "produkt_tu_stunde_19930101_20001231_00433.txt",
                _produkt_text([_row("00433", "1993050113", "12.0")]).getvalue().decode(),
            )
            z.writestr(
                "produkt_tu_stunde_20010101_20251231_00433.txt",
                _produkt_text([_row("00433", "2001050113", "18.0")]).getvalue().decode(),
            )
        df = _station_frame(zpath)
        assert df.height == 2  # both periods concatenated
        assert df["TT_TU"].to_list() == [12.0, 18.0]
        assert df["MESS_DATUM"].dtype == pl.String

    def test_no_produkt_raises(self, tmp_path):
        zpath = tmp_path / "empty.zip"
        with zipfile.ZipFile(zpath, "w") as z:
            z.writestr("Metadaten_Geographie_00433.txt", "junk")
        with pytest.raises(ValueError, match="no produkt_tu_stunde"):
            _station_frame(zpath)


class TestBuildDwdPanel:
    def test_panel_shape_and_start_filter(self, tmp_path):
        slots = [
            ("2024030100", "1.0"),
            ("2024030101", "2.0"),
            ("2024030102", "3.0"),
            ("2024030103", "4.0"),
        ]
        cache = tmp_path / "hourly.parquet"
        pl.concat(
            [
                _to_long(_produkt_df([_row(sid, ts, v) for ts, v in slots]), sid)
                for sid in ("00433", "01975")
            ]
        ).write_parquet(cache)

        grid, _, series = build_dwd_panel(cache, start="2024-03-01", end=None)
        assert sorted(series) == [
            "air_temperature/00433",
            "air_temperature/01975",
        ]
        assert len(grid) == 4
        assert all(len(v) == len(grid) for v in series.values())
        assert np.isfinite(series["air_temperature/00433"]).all()

    def test_end_filter_is_exclusive(self, tmp_path):
        rows = [_row("00433", t, "1.0") for t in ("2024030100", "2024030101", "2024030102")]
        cache = tmp_path / "hourly.parquet"
        _to_long(_produkt_df(rows), "00433").write_parquet(cache)
        grid, _, _ = build_dwd_panel(cache, start=None, end="2024-03-01 02:00")
        assert len(grid) == 2  # 00:00 and 01:00; 02:00 excluded


def test_missing_constant():
    assert MISSING == -999.0
