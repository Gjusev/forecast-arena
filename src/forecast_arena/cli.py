"""forecast-arena CLI: build data, run benchmarks, summarize results."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from forecast_arena.utils.logging import setup_logging

EXPERIMENTS = {
    "01": Path("experiments/01-train-delays"),
    "02": Path("experiments/02-electricity-prices"),
    "03": Path("experiments/03-dwd-weather"),
    "04": Path("experiments/04-renewables"),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="arena", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build-data", help="download raw + build aggregates")
    p_build.add_argument("exp", choices=sorted(EXPERIMENTS))
    p_build.add_argument("--raw-dir", default=None, help="override raw data location")

    p_run = sub.add_parser("run", help="run a benchmark tier")
    p_run.add_argument("exp", choices=sorted(EXPERIMENTS))
    p_run.add_argument("--tier", required=True, choices=["smoke", "pilot", "full"])
    p_run.add_argument("--models", nargs="*", default=None, help="override config model list")

    p_sum = sub.add_parser("summarize", help="recompute metrics from stored predictions")
    p_sum.add_argument("exp", choices=sorted(EXPERIMENTS))
    p_sum.add_argument("--tier", required=True)

    args = parser.parse_args(argv)
    setup_logging()
    log = logging.getLogger("arena")

    base = EXPERIMENTS[args.exp]
    cfg_path = base / "config.yaml"

    if args.cmd == "build-data":
        from forecast_arena.config import load_config
        from forecast_arena.data.db_delays import build_hourly_aggregates
        from forecast_arena.data.electricity import build_price_panel

        cfg = load_config(cfg_path)
        if cfg["experiment"] == "train-delays":
            import glob

            raw = args.raw_dir or cfg["data"]["raw_dir"]
            # resolve HF cache if raw dir holds a snapshot pointer
            if not glob.glob(str(Path(raw) / "monthly_processed_data" / "*.parquet")):
                from huggingface_hub import snapshot_download

                snap = snapshot_download(
                    repo_id="piebro/deutsche-bahn-data",
                    repo_type="dataset",
                    allow_patterns=["monthly_processed_data/*.parquet"],
                    max_workers=4,
                )
                raw = snap
            out = build_hourly_aggregates(Path(raw), Path(cfg["data"]["aggregates"]))
            log.info("aggregates -> %s", out)
        elif cfg["experiment"] == "dwd_weather":
            from forecast_arena.data.dwd import refresh_raw

            out = refresh_raw(Path(args.raw_dir or cfg["data"]["raw_dir"]))
            log.info("dwd hourly cache -> %s", out)
        elif cfg["experiment"] == "renewables":
            from forecast_arena.data.energy_charts import refresh_raw

            out = refresh_raw(Path(args.raw_dir or cfg["data"]["raw_dir"]))
            log.info("renewables hourly cache -> %s", out)
        else:
            out = build_price_panel(Path(cfg["data"]["prices"]), refresh=False)
            log.info(
                "prices cached: %d rows %s -> %s",
                out.height,
                out["timestamp"].min(),
                out["timestamp"].max(),
            )
        return 0

    if args.cmd == "run":
        from forecast_arena.experiment import run_experiment

        out = run_experiment(cfg_path, args.tier, models_override=args.models)
        log.info("done: %s", out)
        return 0

    if args.cmd == "summarize":
        import polars as pl

        from forecast_arena.config import load_config
        from forecast_arena.evaluation.runner import summarize

        cfg = load_config(cfg_path)
        out_dir = Path(cfg.get("results_dir", base / "results"))
        preds = pl.read_parquet(out_dir / "predictions.parquet").filter(pl.col("tier") == args.tier)
        summary = summarize(
            preds,
            cfg.get("protocol", {}).get("eval_horizons", [1, 3, 6, 24]),
            baseline_model=cfg.get("baseline_model", "seasonal_naive_24h"),
        )
        summary.write_parquet(out_dir / f"metrics_{args.tier}.parquet")
        with pl.Config(tbl_rows=40, fmt_str_lengths=40):
            print(summary)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
