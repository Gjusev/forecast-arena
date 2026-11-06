"""Research probe 3: Berlin eva, status semantics, delay distribution, coverage span."""

import duckdb

BASE = "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main"
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
u = f"{BASE}/monthly_processed_data_change/data-2024-10.parquet"

print("=== BERLIN stations ===")
for r in con.execute(f"""
    SELECT eva, station_name, count(*) FROM read_parquet('{u}')
    WHERE station_name ILIKE 'berlin%'
      AND (station_name ILIKE '%bf%' OR station_name ILIKE 'Hauptbahnhof%')
    GROUP BY eva, station_name ORDER BY count(*) DESC LIMIT 8
""").fetchall():
    print(f"  {r[0]}  {r[1]:40s} {r[2]:,}")

print("\n=== arrival_change_status values (one station: Frankfurt 08000105) ===")
for r in con.execute(f"""
    SELECT arrival_change_status, count(*) AS n,
           count(arrival_change_time) AS with_change_time,
           count(arrival_cancellation_time) AS with_cancel
    FROM read_parquet('{u}') WHERE eva='08000105'
    GROUP BY arrival_change_status ORDER BY n DESC
""").fetchall():
    print(f"  status={str(r[0]):30s} n={r[1]:,}  change_time={r[2]:,}  cancel_time={r[3]:,}")

print("\n=== latest snapshot only: Frankfurt arrivals sample ===")
for r in con.execute(f"""
    SELECT id, snapshot_timestamp, arrival_planned_time, arrival_change_time,
           arrival_cancellation_time, arrival_change_status, train_type, train_number
    FROM read_parquet('{u}')
    WHERE eva='08000105' AND arrival_planned_time IS NOT NULL
      AND arrival_planned_time BETWEEN TIMESTAMP '2024-10-15 08:00' AND TIMESTAMP '2024-10-15 09:00'
    ORDER BY arrival_planned_time LIMIT 12
""").fetchall():
    print(" ", r)

print("\n=== distinct snapshot cadence (one week) ===")
for r in con.execute(f"""
    SELECT DISTINCT snapshot_timestamp FROM read_parquet('{u}')
    WHERE snapshot_timestamp BETWEEN TIMESTAMP '2024-10-14' AND TIMESTAMP '2024-10-16'
    ORDER BY 1
""").fetchall():
    print(" ", r[0])
