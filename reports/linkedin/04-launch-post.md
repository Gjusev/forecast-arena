# LinkedIn launch post (draft, not approved for posting)

Format modelled on a post that performed well (short lines, "lazy guess" framing,
CAPS section headers, a "BUT" turn). All numbers from committed results:
per-100 figures = model MAE / seasonal-naive MAE (trains h=1, power pooled).

Media: upload `assets/video/forecast-arena.mp4` natively (no link preview), or the
five stills in `assets/video/stills/` as a carousel. Links go in the first comment.

## Short version (recommended)

We put Mistral's Timestral against Amazon and Google on real German data.
Nearly 2,000 forecasts. The result split in two:

Quick context: Claude predicts the next word. Timestral, Chronos-2 and TimesFM predict the next numbers in a series. No training needed, and they run on a normal CPU.

Each model was scored against a lazy guess that copies yesterday forward.

ELECTRICITY PRICES, 1,408 DAYS
For every €100 the lazy guess was off by:

- Amazon Chronos-2: €68
- Mistral Timestral: €69
- Google TimesFM: €70
- XGBoost: €83
- Microsoft LightGBM: €86

Following Chronos-2 to pick the cheapest hours saved €40 a day.

BUT - on train delays, the AI advantage vanished.

The best AI model and a model trained on a laptop ended up 4 seconds apart.

And on the worst hour of the test (Frankfurt Hbf, 61 min average delay), all six models predicted under 8.

My takeaway: pretrained forecasting shines where data has rhythm. Where it doesn't, cheap models do just as well.

New this week: the arena now covers German weather stations and wind + solar generation with the same protocol. Early runs are live.

Code, data and every forecast are open. Replay any of them in the demo (link in comments).

## Long version

---

We tested Mistral's Timestral against Amazon and Google on real German data
Trains and electricity prices. Nearly 2,000 forecasts.
The results split in two. Data below:

For context, Timestral is a time series prediction model

- Claude and ChatGPT predict the next word. Timestral, Chronos-2 and TimesFM predict the next numbers in a series
- They come pretrained: no training on your data, you just hand them the history
- Each gives a forecast plus an 80% range it expects the real number to land in
- We ran every model on a normal CPU. No GPU

We tested two things Germany runs on:

- Electricity prices for every hour of tomorrow, predicted before the market closes
- Average train delay at 5 big Deutsche Bahn stations, 1 hour ahead
- Every model saw exactly the same past data. No peeking at the future
- Each model is scored against a lazy guess that copies yesterday forward

ELECTRICITY PRICES, 1,408 DAYS
For every €100 the lazy guess was off by:

- Amazon Chronos-2 was off by €68
- Mistral Timestral 209M by €69
- Google TimesFM by €70
- Mistral Timestral 28M (7x smaller) by €70
- XGBoost by €83
- Microsoft LightGBM by €86

When prices went below zero (too much sun and wind):

- Timestral caught about 1 in 2 of those hours
- LightGBM caught 1 in 9

And the 80% ranges of the pretrained models held 76 to 79% of real prices. Almost exactly what they promise.

It pays, too. Shifting 4 MWh of daily power use to the hours Chronos-2 called cheapest saved €40 a day (−17%). That's 74% of what knowing the future would have saved. (Wholesale prices only, not your home bill.)

BUT - on trains, a completely different story...

TRAIN DELAYS, 550 FORECASTS
For every 100 minutes the lazy guess was off by:

- Mistral Timestral 209M was off by 67
- Mistral Timestral 28M by 68
- Amazon Chronos-2 by 69
- Google TimesFM by 69
- Microsoft LightGBM by 69
- XGBoost by 70

The best AI model and a model trained on a laptop: 4 seconds apart.

And the worst hour of the whole test:

- Frankfurt Hbf, 5 February 2026
- Average delay hit 61 minutes
- All six models predicted between 1.5 and 7.1

My read on why:

- Power prices have strong rhythms (sun, wind, weekdays). Pretrained models have seen millions of shapes like that
- Train delays are mostly noise plus sudden incidents. No model that only reads history sees a broken signal box coming

So pretrained forecasting models are a real upgrade where the data has rhythm. Where it doesn't, a cheap model does just as well.

Everything is open: code, data and every single forecast. You can replay any of them, bet on which model wins, then reveal what really happened (link in comments).

---

## First comment

Replay any forecast and bet on the winner: https://huggingface.co/spaces/Gjusev/forecast-arena
Code, data and full reports: https://github.com/Gjusev/forecast-arena

## Fact sheet (for replies)

| Claim | Source |
|---|---|
| Power per-€100: 68.3 / 69.3 / 70.3 / 70.3 / 83.3 / 85.6 | MAE ÷ naive 28.20, `metrics_full.parquet` (02) |
| Trains per-100: 66.8 / 67.6 / 68.6 / 68.6 / 69.3 / 69.8 | MAE ÷ naive 2.76 at h=1 (01) |
| Below-zero hours caught: Timestral 209M recall 0.49, LightGBM 0.115 | `neg_detection_pooled.parquet` |
| 80% range coverage, power: 76.5–79.5% (GBMs give no range) | `coverage_80`, metrics 02 |
| −40.2 €/day, −17%, 74.4% of oracle | `scheduling.json` |
| "4 seconds apart": 1.845 vs 1.915 min = 0.07 min ≈ 4.2 s | metrics 01, h=1 |
| Frankfurt 61 min, forecasts 1.5–7.1 | worst h=1 hour across all stations, `story.json` |
| All models on CPU | run manifests |
