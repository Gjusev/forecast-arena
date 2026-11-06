"""Research probe: snapshot semantics + stations in piebro/deutsche-bahn-data."""

import duckdb

BASE = "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main"
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
u_main = f"{BASE}/monthly_processed_data/data-2024-10.parquet"
u_change = f"{BASE}/monthly_processed_data_change/data-2024-10.parquet"
u_plan = f"{BASE}/monthly_processed_data_plan/data-2024-10.parquet"

for name, url in [("main", u_main), ("change", u_change), ("plan", u_plan)]:
    n = con.execute(f"SELECT count(*) FROM read_parquet('{url}')").fetchone()[0]
    print(f"rows {name} 2024-10: {n:,}")

print("\n=== SNAPSHOT SEMANTICS (change, 2024-10) ===")
r = con.execute(f"""
    SELECT count(DISTINCT snapshot_timestamp) AS n_snapshots,
           min(snapshot_timestamp) AS t_min, max(snapshot_timestamp) AS t_max
    FROM read_parquet('{u_change}')
""").fetchone()
print(f"distinct snapshots: {r[0]}  range: {r[1]} .. {r[2]}")

# rows per train stop: does one stop appear in multiple snapshots?
r = con.execute(f"""
    WITH per_id AS (
        SELECT id, count(*) AS n
        FROM read_parquet('{u_change}')
        GROUP BY id
    )
    SELECT max(n), avg(n), count(*) FROM per_id
""").fetchone()
print(f"rows per id: max={r[0]} avg={r[1]:.2f} distinct ids={r[2]:,}")

print("\n=== STATIONS (change, 2024-10) ===")
stations = con.execute(f"""
    SELECT eva, station_name, count(*) AS n
    FROM read_parquet('{u_change}')
    WHERE lower(station_name) IN (
        'frankfurt(main)hbf','koeln hbf','muenchen hbf','berlin hbf','hamburg hbf'
    ) OR station_name ILIKE '%hbf%'
    GROUP BY eva, station_name
    ORDER BY n DESC
    LIMIT 25
""").fetchall()
for s in stations:
    print(f"  {s[0]}  {s[1]:35s} {s[2]:,}")
