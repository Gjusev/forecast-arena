"""Fetch SMARD day-ahead prices + actual load to local cache parquet."""

from pathlib import Path

from forecast_arena.data.electricity import build_load_actual_panel, build_price_panel

data = Path("data/raw/electricity")
prices = build_price_panel(data / "smard_prices_hourly.parquet", refresh=True)
print("prices:", prices.height, prices["timestamp"].min(), "->", prices["timestamp"].max())
load = build_load_actual_panel(data / "smard_load_hourly.parquet", refresh=True)
print("load:", load.height, load["timestamp"].min(), "->", load["timestamp"].max())
