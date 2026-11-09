# Experiment 06 — League of Legends gold-difference comebacks

**Working title:** *Can a forecasting model smell a comeback at minute 15?*

## Research question

Give a model the first 15 game-minutes of a ranked League of Legends match — the gold-difference curve (blue totalGold − red totalGold, one point per 60-second frame) — and ask for the next 20 minutes. Do zero-shot foundation models anticipate comebacks (a team clearly behind at minute 15 that pulls level by minute 35) better than classical baselines?

**Honesty first:** comeback prediction is not a new task. Prior academic work — an ETRI study (Electronics and Telecommunications Research Institute, published October 2026) — already predicts comebacks in professional LoL from engineered features. We cite it as prior art; our delta is not the task but the comparison: zero-shot foundation models (Timestral, Chronos-2, TimesFM) against classical baselines (persistence, drift). The repo's GBM baselines are excluded: their lag features need 337 points of history and a match offers only 15 under a pre-registered protocol on public data.

## Dataset

[Hugging Face: AngryBacteria/league_of_legends](https://huggingface.co/datasets/AngryBacteria/league_of_legends) (Riot Games Match-V5 data collected via the official Riot API), license **Apache-2.0**. 12,719 matches spanning patches 13.x–14.x; the benchmark keeps **ranked queues only** (420 solo/duo, 440 flex — 5,285 matches): ARAM and Arena gold curves are a different process and are excluded. Two MongoDB extended-JSON exports, streamed (never loaded whole):

- `match_v5.json` (1.3 GB) — per-match summary: gameCreation, gameDuration, patch, queueId, teams, participants.
- `timeline_v5.json` (14.4 GB) — per-match timeline, one frame per 60 s game-minute; `info.frames[k].participantFrames["1".."10"].totalGold`, blue = participants 1–5, red = 6–10.

The card says "BSON-JSON format, optimized for MongoDB"; the files are `.json` and the HF viewer's JSON loader parses them, so the loader sniffs the layout (NDJSON vs top-level JSON array) and streams documents from either. Raw BSON is rejected with a clear error.

## Protocol

- **Information cut:** each series is exactly 36 game-minutes (frames 0–35). Models see minutes 0–14 (history), forecast minutes 15–34 (horizon 20). Minute 35 is held out for the reality check.
- **Single origin per match:** `origins() = [15]` (min_train 15, origin_step 10^9). Matches are kept only when all 36 frames exist and all ten participants' `totalGold` are finite at every frame — so every series is complete and the origin is valid for all series at once.
- **Metric:** MAE by horizon h = 1, 5, 10, 15, 20 with skill vs `persistence` (the honest "the gap holds" baseline for a within-match curve; a seasonal-naive on a 36-point game-minute grid is meaningless).
- **Pre-registered comeback rule (fixed before any forecast was computed):** a match is comeback-eligible when `gold_diff` at minute 15 ≤ **−2000** (blue behind by 2000+ gold). Reality flip: actual `gold_diff` ≥ 0 at any game-minute 16..35. A model "predicts" a comeback when its point forecast crosses 0 at any h ≤ 20; `analysis.py` scores precision/recall/F1 of that call against reality, alongside the base rate a constant "always comeback" predictor would achieve.
- Series ids are `gold_diff/<match_id>`; the timestamp grid is synthetic (2000-01-01 00:00 + k·60 s, naive) so game-minutes line up across matches.

## How to run

```bash
uv run arena build-data 06                                  # downloads + cache (~30-60 min, one-time)
uv run --extra ml --extra foundation arena run 06 --tier smoke   # 3 models x 30 matches
uv run --extra ml --extra foundation arena run 06 --tier pilot   # 500 matches
uv run arena summarize 06 --tier pilot
uv run python experiments/06-lol-comebacks/analysis.py
```

Set `PYTHONIOENCODING=utf-8` on Windows shells.

## Results

**Full tier** (all 1,419 ranked matches that reach minute 36, one origin at minute 15, n = 1,419 per horizon). Run 2026-11-09, CPU. Smoke and pilot (500 matches) ran first and agree in direction.

**Point accuracy - skill vs persistence (MAE, %; negative = worse than persistence):**

| model | h=1 | h=5 | h=10 | h=15 | h=20 |
|---|---|---|---|---|---|
| drift | -5.7 | -15.7 | -16.4 | -16.6 | -12.8 |
| timestral_209M | -6.1 | -4.0 | -3.3 | -4.6 | -3.8 |
| timestral_28M | -6.9 | -5.6 | -4.7 | -6.4 | -5.0 |
| chronos_2 | -6.4 | -6.8 | -10.6 | -6.7 | -2.5 |
| timesfm_3_0 | -9.8 | -11.8 | -14.0 | -17.9 | -17.8 |

Persistence MAE (gold): 736 / 1,673 / 2,535 / 3,185 / 4,203 at h = 1 / 5 / 10 / 15 / 20. **No model beats persistence at any horizon.** The zero-shot foundation models (Timestral, Chronos-2) are closest, 2-10% worse; drift and TimesFM 3.0 are 6-18% worse.

**Comeback call (pre-registered rule):** 383 of the 1,419 matches were eligible (blue >= 2,000 gold behind at minute 15); 199 flipped (base rate **52.0%**).

| model | predicted | TP | FP | precision | recall | F1 |
|---|---|---|---|---|---|---|
| timesfm_3_0 | 23 | 14 | 9 | 0.609 | 0.070 | 0.126 |
| chronos_2 | 21 | 12 | 9 | 0.571 | 0.060 | 0.109 |
| timestral_28M | 11 | 6 | 5 | 0.545 | 0.030 | 0.057 |
| drift | 9 | 5 | 4 | 0.556 | 0.025 | 0.048 |
| timestral_209M | 9 | 5 | 4 | 0.556 | 0.025 | 0.048 |
| persistence | 1 | 0 | 1 | 0.000 | 0.000 | 0.000 |

Reading: a constant "always comeback" call would score precision 0.52 / recall 1.0 / F1 ~0.68. Models call a comeback in only 2-6% of eligible matches because a point forecast of a smooth curve rarely crosses zero. Their precision (0.55-0.61) is only marginally above the 0.52 base rate, from 9-23 calls, so it is not distinguishable from chance. (Persistence's single call is possible because minute 14, its last observation, can already be above 0 while minute 15 is <= -2000.) No confidence intervals, one split, matches within a patch are correlated. Conclusion: no evidence that zero-shot models anticipate comebacks beyond a persistence baseline - not proof that they cannot.

## Limitations

- Not pro play: matches are ranked solo/flex (queues 420/440). Pro gold curves are slower and more structured; conclusions may not transfer.
- **Survivorship toward close games:** a match enters the panel only if it reaches minute 36 (~18% of the raw pool do). Short, one-sided stomps are excluded by construction — the comeback base rate here is higher than in all matches, and absolute F1s are not comparable to unfiltered match pools.
- Multi-patch pool: patches 13.x–14.x are pooled; gold dynamics drift patch to patch (the analysis reports the patch mix).
- Cross-match pooling: series are pooled for shared metrics, but matches from the same patch share meta and are correlated — rows are not independent samples.
- 60 s frame resolution: leads that flip and re-flip inside a minute are invisible; "comeback" is defined on minute-resolution gold only.
- Blue side in the experiment always means participants 1–5; side assignment and patch are frozen in the cache, not re-derived per match.
