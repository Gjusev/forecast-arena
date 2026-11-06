"""Research probe: inspect piebro/deutsche-bahn-data monthly processed parquet over HTTP.

Reads only parquet metadata + tiny samples (range requests), never full files.
"""

import duckdb

BASE = "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main"
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")

url = f"{BASE}/monthly_processed_data_change/data-2024-10.parquet"

print("=== SCHEMA (change) ===")
cols = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{url}')").fetchall()
for c in cols:
    print(f"  {c[0]:40s} {c[1]}")

print("\n=== ROW COUNT ===")
n = con.execute(f"SELECT count(*) FROM read_parquet('{url}')").fetchone()[0]
print(f"  rows in 2024-10 (change): {n:,}")
