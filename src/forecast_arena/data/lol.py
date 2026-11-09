"""League of Legends gold curve for experiment 06 (comeback forecasting).

Source: HF dataset ``AngryBacteria/league_of_legends`` (Riot Match-V5 exports
via the official Riot API), license **Apache-2.0**. Two files: ``match_v5.json``
(1.3 GB) and ``timeline_v5.json`` (14.4 GB).

The export is a MongoDB extended-JSON dump (verified on disk: top-level JSON
array, numbers wrapped as ``{"$numberLong": "166..."}``, ids as
``metadata.matchId``). ``_iter_documents`` sniffs the first non-whitespace byte
and streams documents from a top-level array or NDJSON; raw BSON is rejected
with a clear error. Nothing is ever loaded whole into memory.

Cache: one row per (match, frame) with ``ts`` = synthetic grid minute
(2000-01-01 00:00 + k * 60 s; minute k = game-minute index k), ``value`` =
blue totalGold - red totalGold, ``target`` = "gold_diff", ``zone`` = match_id.
Matches are kept only with >= 36 frames and finite team golds at every frame
0..35, so every series is exactly 36 points and the protocol's single origin
at minute 15 is valid for all series at once.
"""

from __future__ import annotations

import json
import logging
import math
import re
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl
from huggingface_hub import hf_hub_download

log = logging.getLogger(__name__)

REPO = "AngryBacteria/league_of_legends"
MATCH_FILE = "match_v5.json"
TIMELINE_FILE = "timeline_v5.json"
SUMMARY_NAME = "matches_summary.parquet"
CACHE_NAME = "lol_gold_minute.parquet"

TARGET = "gold_diff"
EPOCH = datetime(2000, 1, 1)  # synthetic grid: minute k -> EPOCH + k * 60 s
MIN_FRAMES = 36  # need frames 0..35: 15 train minutes + 20 forecast + minute 35 actual

# a "complete file" heuristic: both files are way over 1 GB; partial leftovers are not
_COMPLETE_BYTES = 1_000_000_000
_SNIFF_BYTES = 1 << 24  # 16 MB window for the layout sniff
_CHUNK = 1 << 22  # 4 MB streaming chunks

_STR = re.compile(rb'"(?:[^"\\]|\\.)*"')  # one complete JSON string (escapes honored)
_DELIM = re.compile(rb'["{}]')  # structural characters outside strings


def _iter_array_docs(path: Path, chunk: int = _CHUNK) -> Iterator[dict]:
    """Stream documents from a top-level JSON array without loading the file.

    Brace-depth state machine; string literals are skipped with a regex so
    braces inside strings cannot break the depth count. Buffer rules: compact
    (drop the scanned prefix, ``data = data[i:]``) ONLY while no document is
    open (depth == 0, so ``start`` is always None then); while a document is
    open, refills APPEND so ``start`` and ``i`` stay valid. Guaranteed
    progress: every refill either advances the scan or hits EOF and raises.
    """
    depth = 0
    start = None
    i = 0
    eof = False
    with open(path, "rb") as f:
        head = f.read(chunk)
        pos = head.find(b"[")
        if pos < 0:
            raise ValueError(f"{path.name}: no top-level '[' - not a JSON array")
        data = head[pos + 1 :]
        while True:
            if not eof and len(data) - i < chunk // 2:
                more = f.read(chunk)
                if not more:
                    eof = True
                elif depth > 0:
                    # doc open: drop the prefix before it (bounded buffer), keep start/i valid
                    data = data[start:] + more
                    i -= start
                    start = 0
                    continue
                else:
                    data = data[i:] + more  # compact: no doc open, start None
                    i = 0
                    continue
            m = _DELIM.search(data, i)
            if m is None:
                if eof:
                    break
                more = f.read(chunk)
                if not more:
                    eof = True
                else:
                    data = data + more  # append only: never drop an open doc
                continue
            j = m.start()
            c = data[j : j + 1]
            if c == b"{":
                if depth == 0:
                    start = j
                depth += 1
                i = j + 1
            elif c == b"}":
                depth -= 1
                if depth == 0:
                    doc = bytes(data[start : j + 1])
                    start = None
                    yield json.loads(doc)
                i = j + 1
            else:  # '"' opening a real string (structural chars processed in order)
                s = _STR.match(data, j)
                if s is not None:
                    i = s.end()  # skip past the complete string
                    continue
                # string continues past the buffer: append more and retry
                if eof:
                    raise ValueError(f"{path.name}: unterminated string at end of file")
                more = f.read(chunk)
                if not more:
                    raise ValueError(f"{path.name}: unterminated string at end of file")
                data = data + more
                i = j  # retry the same quote after appending
        if depth != 0:
            raise ValueError(f"{path.name}: truncated JSON array (depth {depth} at EOF)")


def _iter_ndjson_docs(path: Path) -> Iterator[dict]:
    """Stream documents from newline-delimited JSON, one json.loads per line."""
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{lineno}: invalid JSON ({exc})") from exc


def _iter_documents(path: Path) -> Iterator[dict]:
    """Sniff the layout from the first bytes, then stream documents off it.

    ``[`` -> top-level array, ``{`` with a newline in the sniff window -> NDJSON,
    ``{`` alone -> one compact document (unstreamable), anything else -> raw
    BSON, which we refuse with a clear error.
    """
    with open(path, "rb") as f:
        head = f.read(_SNIFF_BYTES)
    head = head.lstrip()
    if head[:1] == b"[":
        yield from _iter_array_docs(path)
    elif head[:1] == b"{":
        if b"\n" in head:
            yield from _iter_ndjson_docs(path)
        else:
            raise ValueError(f"{path.name}: single compact JSON document cannot be streamed")
    else:
        raise ValueError(f"{path.name}: not JSON text (raw BSON or other binary)")


def _num(v: object) -> float | None:
    """MongoDB extended-JSON number -> float; missing/invalid/non-finite -> None."""
    if isinstance(v, dict):
        for key in ("$numberLong", "$numberInt", "$numberDouble"):
            if key in v:
                v = v[key]
                break
        else:
            return None
    if isinstance(v, bool):  # bool is an int subclass; never a gold value
        return None
    if isinstance(v, str):
        try:
            v = float(v)
        except ValueError:
            return None
    if isinstance(v, (int, float)):
        out = float(v)
        return out if math.isfinite(out) else None
    return None


def _match_id(doc: dict) -> str | None:
    """metadata.matchId / metadata.match_id, else int(info.gameId) as string."""
    meta = doc.get("metadata") or {}
    if isinstance(meta, dict):
        mid = meta.get("matchId") or meta.get("match_id")
        if mid is not None:
            return str(mid)
    gid = _num((doc.get("info") or {}).get("gameId"))
    return str(int(gid)) if gid is not None else None


def _summary_row(doc: dict) -> dict | None:
    """Match summary: id, creation ms, duration minutes, patch, queue id."""
    mid = _match_id(doc)
    if mid is None:
        return None
    info = doc.get("info") or {}
    gc = _num(info.get("gameCreation"))
    dur = _num(info.get("gameDuration"))
    return {
        "match_id": mid,
        "game_creation": int(gc) if gc else None,
        "duration_min": dur / 60 if dur else None,
        "patch": info.get("patch") or info.get("gameVersion"),
        "queue_id": info.get("queueId"),
    }


def _gold_curve(doc: dict) -> tuple[str, list[float]] | None:
    """36 per-minute gold diffs (blue 1-5 minus red 6-10), or None if unusable.

    Frames are indexed by position (minute k = frame k), not by their
    ``timestamp`` field - Riot exports may skip minute 0. Any match with fewer
    than MIN_FRAMES frames, a missing participant cell, or a non-finite gold
    at any frame is dropped whole, so kept series are always 36 finite points.
    """
    mid = _match_id(doc)
    if mid is None:
        return None
    frames = (doc.get("info") or {}).get("frames") or []
    if len(frames) < MIN_FRAMES:
        return None
    diffs = []
    for frame in frames[:MIN_FRAMES]:
        pf = frame.get("participantFrames") or {}
        parts = []
        for p in range(1, 11):
            cell = pf.get(str(p), pf.get(p))
            gold = _num(cell.get("totalGold")) if isinstance(cell, dict) else None
            if gold is None:
                return None
            parts.append(gold)
        diffs.append(sum(parts[:5]) - sum(parts[5:]))
    return str(mid), diffs


def _ensure_file(raw_dir: Path, name: str) -> Path:
    """Local path for a dataset file; download via HF only if not already there."""
    raw_dir = Path(raw_dir)
    path = raw_dir / name
    if path.exists() and path.stat().st_size > _COMPLETE_BYTES:
        return path
    return Path(
        hf_hub_download(
            repo_id=REPO,
            filename=name,
            repo_type="dataset",
            local_dir=raw_dir,
        )
    )


def refresh_raw(raw_dir: Path) -> Path:
    """Fetch both Riot exports and build the per-minute gold-diff cache.

    Streams each file through ``_iter_documents`` (never loaded whole), caches
    the summary parquet and the long-format gold cache independently, so a
    rerun skips whichever stage is already on disk.
    """
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    summary = raw_dir / SUMMARY_NAME
    cache = raw_dir / CACHE_NAME
    match_path = _ensure_file(raw_dir, MATCH_FILE)
    if not summary.exists():
        rows: list[dict] = []
        for n, doc in enumerate(_iter_documents(match_path), 1):
            row = _summary_row(doc)
            if row is not None:
                rows.append(row)
            if n % 1000 == 0:
                print(f"lol: match summaries {n} scanned, {len(rows)} usable", flush=True)
        pl.DataFrame(rows).write_parquet(summary)
    if cache.exists():
        return cache
    timeline_path = _ensure_file(raw_dir, TIMELINE_FILE)
    curves: dict[str, list[float]] = {}
    kept = 0
    for n, doc in enumerate(_iter_documents(timeline_path), 1):
        curve = _gold_curve(doc)
        if curve is not None:
            curves[curve[0]] = curve[1]
            kept += 1
        if n % 1000 == 0:
            print(f"lol: timelines {n} scanned, {kept} kept", flush=True)
    rows = []
    for mid, diffs in curves.items():
        for k, v in enumerate(diffs):
            rows.append(
                {"ts": EPOCH + timedelta(minutes=k), "value": v, "target": TARGET, "zone": mid}
            )
    df = pl.DataFrame(rows).sort(["zone", "ts"])
    df.write_parquet(cache)
    print(
        f"lol: cache {df.height} rows ({kept} matches x {MIN_FRAMES} minutes) -> {cache}",
        flush=True,
    )
    return cache


RANKED_QUEUES = (420, 440)  # ranked solo/duo + flex: lane-phase LoL; ARAM/Arena excluded


def ranked_match_ids(raw_dir: Path) -> set[str] | None:
    """Match ids in RANKED_QUEUES from the summary; None when no summary exists."""
    summary = Path(raw_dir) / SUMMARY_NAME
    if not summary.exists():
        return None
    s = pl.read_parquet(summary)
    return set(s.filter(pl.col("queue_id").is_in(RANKED_QUEUES))["match_id"].to_list())


def build_lol_panel(
    hourly_path: Path,
    start: str | None = None,
    end: str | None = None,
) -> tuple[list, np.ndarray, dict[str, np.ndarray]]:
    """Gold cache -> panel via grid_and_series; ids like 'gold_diff/EUW1_1'.

    When the sibling matches_summary.parquet exists, only ranked matches
    (RANKED_QUEUES) are kept: ARAM/Arena gold curves are a different process.
    """
    from forecast_arena.data.panels import grid_and_series

    df = pl.read_parquet(hourly_path)
    keep = ranked_match_ids(Path(hourly_path).parent)
    if keep is not None:
        before = df["zone"].n_unique()
        df = df.filter(pl.col("zone").is_in(keep))
        log.info(
            "lol panel: %d -> %d ranked matches (of %d)", before, df["zone"].n_unique(), before
        )
    if start:
        df = df.filter(pl.col("ts") >= pl.lit(start).str.to_datetime())
    if end:
        df = df.filter(pl.col("ts") < pl.lit(end).str.to_datetime())
    return grid_and_series(df, "ts", ["target", "zone"], "value")
