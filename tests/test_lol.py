"""Offline tests for experiment 06: LoL gold-curve extraction + panel building.

The inline fixtures mirror the Riot Match-V5 timeline layout used by the
AngryBacteria/league_of_legends export: one JSON document per match with
info.frames[k].participantFrames["1".."10"].totalGold (blue = 1-5, red = 6-10).
No downloads; everything runs on tmp_path fixtures.
"""

import json
import math
from datetime import timedelta

import numpy as np
import polars as pl
import pytest

from forecast_arena.data.lol import (
    EPOCH,
    MIN_FRAMES,
    TARGET,
    _gold_curve,
    _iter_array_docs,
    _iter_documents,
    _summary_row,
    build_lol_panel,
)


def _frame(k: int, blue_gold: int, red_gold: int) -> dict:
    pf = {str(i): {"participantId": i, "totalGold": blue_gold + i} for i in range(1, 6)}
    for i in range(6, 11):
        pf[str(i)] = {"participantId": i, "totalGold": red_gold + i}
    return {"timestamp": k * 60000, "participantFrames": pf, "events": []}


def _timeline_doc(
    match_id: str = "EUW1_1",
    n_frames: int = MIN_FRAMES,
    gap: int = 3000,
    missing_participant_at: int | None = None,
    null_gold_at: int | None = None,
) -> dict:
    frames = []
    for k in range(n_frames):
        blue = 15000 + k * 100
        f = _frame(k, blue, blue - gap)
        if missing_participant_at == k:
            del f["participantFrames"]["10"]
        if null_gold_at == k:
            f["participantFrames"]["3"]["totalGold"] = None
        frames.append(f)
    return {"metadata": {"match_id": match_id}, "info": {"frames": frames, "frameInterval": 60000}}


# blue sum = 5*blue + (1+2+3+4+5) = 5*blue + 15; red sum = 5*red + (6+7+8+9+10) = 5*red + 40
# gold_diff = (5*blue + 15) - (5*red + 40) = 5*gap - 25, constant per frame here
DIFF = 5 * 3000 - 25  # 14975


class TestGoldCurve:
    def test_extracts_36_gold_diffs(self):
        mid, diffs = _gold_curve(_timeline_doc())
        assert mid == "EUW1_1"
        assert len(diffs) == MIN_FRAMES
        assert diffs == [float(DIFF)] * MIN_FRAMES

    def test_rejects_short_match(self):
        assert _gold_curve(_timeline_doc(n_frames=MIN_FRAMES - 1)) is None

    def test_rejects_missing_participant(self):
        assert _gold_curve(_timeline_doc(missing_participant_at=10)) is None

    def test_rejects_null_gold(self):
        assert _gold_curve(_timeline_doc(null_gold_at=0)) is None

    def test_frame_index_not_timestamp(self):
        # frames starting at timestamp 60000 (Riot skips minute 0) still map k -> minute k
        doc = _timeline_doc()
        for k, frame in enumerate(doc["info"]["frames"]):
            frame["timestamp"] = (k + 1) * 60000
        _, diffs = _gold_curve(doc)
        assert diffs == [float(DIFF)] * MIN_FRAMES


class TestSummaryRow:
    def test_summary_fields(self):
        doc = {
            "metadata": {"match_id": "EUW1_2"},
            "info": {
                "gameCreation": 1700000000000,
                "gameDuration": 2100,
                "patch": "14.13",
                "queueId": 440,
            },
        }
        assert _summary_row(doc) == {
            "match_id": "EUW1_2",
            "game_creation": 1700000000000,
            "duration_min": 35.0,
            "patch": "14.13",
            "queue_id": 440,
        }

    def test_game_id_fallback_and_missing(self):
        assert _summary_row({"info": {"gameId": 42}})["match_id"] == "42"
        assert _summary_row({"info": {}}) is None

    def test_mongodb_extended_json(self):
        doc = {
            "_id": {"$oid": "abc"},
            "metadata": {"dataVersion": "2", "matchId": "EUW1_7"},
            "info": {
                "gameCreation": {"$numberLong": "1700000000000"},
                "gameDuration": 2100,
                "gameId": {"$numberLong": "12345"},
                "gameVersion": "14.13",
                "queueId": 440,
            },
        }
        row = _summary_row(doc)
        assert row["match_id"] == "EUW1_7"
        assert row["game_creation"] == 1700000000000
        assert row["duration_min"] == 35.0
        assert row["patch"] == "14.13"

    def test_extended_json_gold(self):
        doc = _timeline_doc()
        doc["metadata"] = {"matchId": "EUW1_9"}
        for frame in doc["info"]["frames"]:
            for cell in frame["participantFrames"].values():
                cell["totalGold"] = {"$numberLong": str(cell["totalGold"])}
        mid, diffs = _gold_curve(doc)
        assert mid == "EUW1_9"
        assert diffs == [float(DIFF)] * MIN_FRAMES


class TestIterDocuments:
    def test_ndjson(self, tmp_path):
        docs = [_timeline_doc("EUW1_1"), _timeline_doc("EUW1_2")]
        p = tmp_path / "t.json"
        p.write_bytes(b"\n".join(json.dumps(d).encode() for d in docs) + b"\n")
        assert list(_iter_documents(p)) == docs

    def test_json_array(self, tmp_path):
        docs = [_timeline_doc("EUW1_1"), _timeline_doc("EUW1_2")]
        p = tmp_path / "t.json"
        p.write_bytes(b"[\n" + b",\n".join(json.dumps(d).encode() for d in docs) + b"\n]\n")
        assert list(_iter_documents(p)) == docs

    def test_array_chunk_boundaries(self, tmp_path):
        # tiny chunk forces refuels inside strings; the strings carry braces and
        # escaped quotes that must not confuse the depth counter
        docs = [
            {**_timeline_doc("EUW1_1"), "note": 'brace { } "quoted" { "x": 1 } end'},
            {**_timeline_doc("EUW1_2"), "note": 'esc " backslash \\ brace {'},
        ]
        p = tmp_path / "t.json"
        p.write_bytes(b"[" + b",\n".join(json.dumps(d).encode() for d in docs) + b"]")
        assert list(_iter_array_docs(p, chunk=16)) == docs

    def test_array_buffer_stays_bounded(self, tmp_path):
        # regression: the buffer used to grow with the file (refills landed
        # mid-document, so the scanned prefix was never dropped)
        import tracemalloc

        docs = [{"id": i, "pad": "x" * 3000} for i in range(1600)]  # ~4.8 MB file
        p = tmp_path / "big.json"
        p.write_bytes(b"[" + b",".join(json.dumps(d).encode() for d in docs) + b"]")
        tracemalloc.start()
        n = sum(1 for _ in _iter_array_docs(p, chunk=8192))
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        assert n == 1600
        assert peak < p.stat().st_size // 4, peak  # unbounded growth peaked >= file size

    def test_truncated_inputs_raise(self, tmp_path):
        p1 = tmp_path / "cut_doc.json"
        p1.write_bytes(b'[{"a": 1')  # depth != 0 at EOF
        with pytest.raises(ValueError, match="truncated"):
            list(_iter_array_docs(p1))
        p2 = tmp_path / "cut_str.json"
        p2.write_bytes(b'[{"a": "unterminated]')
        with pytest.raises(ValueError, match="unterminated"):
            list(_iter_array_docs(p2))

    def test_bson_rejected(self, tmp_path):
        p = tmp_path / "bson.json"
        p.write_bytes(b"\x05\x00\x00\x00binary-not-json")
        with pytest.raises(ValueError, match="BSON"):
            list(_iter_documents(p))


def _write_cache(tmp_path, matches: dict[str, list[float]]):
    rows = []
    for mid, diffs in matches.items():
        for k, v in enumerate(diffs):
            rows.append(
                {"ts": EPOCH + timedelta(minutes=k), "value": v, "target": TARGET, "zone": mid}
            )
    path = tmp_path / "cache.parquet"
    pl.DataFrame(rows).write_parquet(path)
    return path


class TestBuildLolPanel:
    def test_panel_shape_and_ids(self, tmp_path):
        a, b = [float(DIFF)] * MIN_FRAMES, [float(-DIFF)] * MIN_FRAMES
        cache = _write_cache(tmp_path, {"EUW1_1": a, "EUW1_2": b})
        grid, _, series = build_lol_panel(cache)
        assert len(grid) == MIN_FRAMES
        assert grid[0] == EPOCH and grid[-1] == EPOCH + timedelta(minutes=MIN_FRAMES - 1)
        assert sorted(series) == ["gold_diff/EUW1_1", "gold_diff/EUW1_2"]
        assert all(len(v) == len(grid) for v in series.values())
        assert list(series["gold_diff/EUW1_1"]) == a
        assert np.isfinite(series["gold_diff/EUW1_2"]).all()

    def test_start_end_filters(self, tmp_path):
        cache = _write_cache(tmp_path, {"EUW1_1": [1.0] * MIN_FRAMES})
        _, _, series = build_lol_panel(cache, start="2000-01-01 00:10:00")
        assert len(series["gold_diff/EUW1_1"]) == MIN_FRAMES - 10  # minutes 10..35
        _, _, series = build_lol_panel(cache, end="2000-01-01 00:20:00")
        assert len(series["gold_diff/EUW1_1"]) == 20  # minutes 0..19, end exclusive

    def test_single_origin_protocol_valid(self, tmp_path):
        # 15 train minutes + 20 forecast steps = minute 35; origins() must yield [15]
        from forecast_arena.evaluation.protocol import PanelSpec

        cache = _write_cache(tmp_path, {"EUW1_1": [1.0] * MIN_FRAMES})
        _, _, series = build_lol_panel(cache)
        spec = PanelSpec(
            series=series, horizon=20, origin_step=1_000_000_000, min_train=15, eval_horizons=[20]
        )
        assert spec.origins() == [15]


def test_constants():
    assert MIN_FRAMES == 36
    assert TARGET == "gold_diff"
    assert math.isfinite(float(DIFF))
