# Data attributions

This project ships code and small derived aggregates only. Raw datasets stay
with their publishers under their own terms:

## Deutsche Bahn timetable data

- Source: https://huggingface.co/datasets/piebro/deutsche-bahn-data
- Original data: Deutsche Bahn AG timetable information, aggregated by the
  dataset author
- License: CC-BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- Use: hourly station aggregates of arrival delays, 2024-07 → 2026-10,
  five major stations

## German day-ahead electricity prices

- Source: SMARD — Marktstammdatenregister / Bundesnetzagentur,
  https://www.smard.de (filter 4169, hourly day-ahead prices DE-LU)
- License: Datenlizenz Deutschland Namensnennung 2.0
  (https://www.govdata.de/dl-de/by-2-0)
- Use: price series 2018-10 → present, benchmark window 2021-01 → 2026-11

## Cross-check source

- energy-charts.info API (price cross-check only; not redistributed)

## Model weights

- mistralai/Timestral-28M, mistralai/Timestral-209M — Mistral AI, Modified
  MIT license (weights), Apache-2.0 (code)
- amazon/chronos-2 — Amazon, Apache-2.0
- google/timesfm-3.0-pytorch — Google, Apache-2.0 (code), model license per
  model card
