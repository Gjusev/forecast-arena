"""Research probe 5: main file schema, coverage, per-station arrivals/day sanity."""

import json
import urllib.request

import duckdb

BASE = "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main"
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
u_main = f"{BASE}/monthly_processed_data/data-2024-10.parquet"

print("=== main file schema ===")
for c in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{u_main}')").fetchall():
    print(f"  {c[0]:40s} {c[1]}")

print("\n=== coverage ===")
for d in ("monthly_processed_data",):
    with urllib.request.urlopen(
        f"https://huggingface.co/api/datasets/piebro/deutsche-bahn-data/tree/main/{d}"
    ) as f:
        files = json.load(f)
    months = sorted(x["path"].split("data-")[1].replace(".parquet", "") for x in files)
    print(f"  {d}: n={len(months)} first={months[0]} last={months[-1]}")

STATIONS = {
    "Frankfurt(Main) Hbf": ["08000105", "08098105"],
    "Köln Hbf": ["08000207"],
    "München Hbf": ["08098263", "08000261"],
    "Berlin Hbf": ["08089021", "08098160", "08011160"],
    "Hamburg Hbf": ["08098549", "08002549"],
}
print("\n=== arrivals/day per station (main file, Oct 2024, rail types only) ===")
eva_list = ",".join(f"'{e}'" for es in STATIONS.values() for e in es)
for r in con.execute(f"""
    SELECT station_name, eva, count(*) AS n,
           count(arrival_planned_time) AS with_arrival
    FROM read_parquet('{u_main}')
    WHERE eva IN ({eva_list})
    GROUP BY station_name, eva ORDER BY station_name, n DESC
""").fetchall():
    per_day = r[2] / 31
    print(f"  {r[0]!r:28s} {r[1]}  rows={r[2]:,} (~{per_day:.0f}/day) arrivals={r[3]:,}")

print("\n=== delay distribution sanity (Frankfurt, non-cancelled arrivals with change) ===")
for r in con.execute(f"""
    SELECT
        count(*) AS n,
        avg(date_diff('second', arrival_planned_time, arrival_change_time)/60.0) AS avg_delay,
        median(date_diff('second', arrival_planned_time, arrival_change_time)/60.0) AS med,
        quantile_cont(date_diff('second', arrival_planned_time, arrival_change_time)/60.0,
                      0.9) AS p90,
        quantile_cont(date_diff('second', arrival_planned_time, arrival_change_time)/60.0,
                      0.99) AS p99
    FROM read_parquet('{u_main}')
    WHERE eva IN ('08000105','08098105')
      AND arrival_planned_time IS NOT NULL AND arrival_change_time IS NOT NULL
      AND arrival_cancellation_time IS NULL
""").fetchall():
    print(f"  n={r[0]:,} avg={r[1]:.1f}min med={r[2]:.1f} p90={r[3]:.1f} p99={r[4]:.1f}")

print("\n=== cancellation encoding in main file ===")
for r in con.execute(f"""
    SELECT count(*) AS n,
           count(arrival_cancellation_time) AS with_cancel_time,
           count(arrival_change_status) AS with_status,
           count(DISTINCT arrival_change_status) AS n_status
    FROM read_parquet('{u_main}')
    WHERE eva IN ('08000105','08098105') AND arrival_planned_time IS NOT NULL
""").fetchall():
    print(f"  arrivals={r[0]:,} cancel_time={r[1]:,} status={r[2]:,} statuses={r[3]}")
