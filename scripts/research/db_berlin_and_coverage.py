"""Research probe 4: Berlin mystery, main-file semantics, coverage span, arrivals/day."""

import json
import urllib.request

import duckdb

BASE = "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main"
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
u_change = f"{BASE}/monthly_processed_data_change/data-2024-10.parquet"
u_main = f"{BASE}/monthly_processed_data/data-2024-10.parquet"

print("=== any station containing 'erlin' ===")
for r in con.execute(f"""
    SELECT eva, station_name, count(*) FROM read_parquet('{u_change}')
    WHERE station_name ILIKE '%erlin%'
    GROUP BY eva, station_name ORDER BY count(*) DESC LIMIT 10
""").fetchall():
    print(f"  {r[0]}  {r[1]!r}  {r[2]:,}")

print("\n=== eva 08010716 (known Berlin Hbf code) ===")
for r in con.execute(f"""
    SELECT eva, station_name, count(*) FROM read_parquet('{u_change}')
    WHERE eva IN ('08010716','8010716','008010716')
    GROUP BY eva, station_name
""").fetchall():
    print(f"  {r[0]}  {r[1]!r}  {r[2]:,}")

print("\n=== main file: one row per id? ===")
r = con.execute(
    f"SELECT count(*), count(DISTINCT id) FROM read_parquet('{u_main}')"
).fetchone()
print(f"  main rows={r[0]:,} distinct ids={r[1]:,}")
r = con.execute(
    f"""SELECT count(DISTINCT snapshot_timestamp) FROM read_parquet('{u_main}')"""
).fetchone()
print(f"  main distinct snapshots={r[0]}")

print("\n=== full monthly coverage (file list) ===")
with urllib.request.urlopen(
    "https://huggingface.co/api/datasets/piebro/deutsche-bahn-data/tree/main/monthly_processed_data"
) as f:
    files = json.load(f)
months = sorted(x["path"].split("data-")[1].replace(".parquet", "") for x in files)
print(f"  n={len(months)}  first={months[0]}  last={months[-1]}")
