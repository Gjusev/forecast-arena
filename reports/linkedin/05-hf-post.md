# Hugging Face post (draft, not approved for posting)

Attach `assets/video/preview.gif` as the image (HF posts don't embed video;
the film autoplays in the Space's Start-here tab).

## Short version (recommended)

We ran almost 2,000 forecasts on real German data to see whether the new AI
forecasting models are actually better.

Timestral, Chronos-2, TimesFM vs LightGBM, XGBoost and two simple baselines - on train delays, electricity prices, weather stations and wind + solar generation.
Every model saw the same data and could not peek at the future. Everything ran
on a CPU.

On electricity prices, the AI models won clearly. For every €100 the "same as
yesterday" guess missed, Chronos-2 missed €68. LightGBM missed €86.

On train delays, it was a tie. Best AI model and best laptop-trained model:
0.07 minutes apart.

And when Frankfurt hit 61 minutes of average delay, every model predicted
under 8. Nobody saw it coming.

You can replay every forecast, bet on the winner, then reveal what really
happened:

Demo: https://huggingface.co/spaces/Gjusev/forecast-arena
Code: https://github.com/Gjusev/forecast-arena

#timeseries #forecasting

## Long version (fallback, for comments/replies)

**We replayed ~2,000 forecasts on real German data to answer one question: do
time series foundation models actually beat classical methods?**

Short answer: it depends on the data — and the split is the interesting part.

⚡ **Electricity prices** (DE-LU day-ahead, 1,408 daily pre-auction origins):
foundation models clearly win. For every €100 the seasonal-naive guess missed,
Chronos-2 missed €68, Timestral 209M €69, XGBoost €83, LightGBM €86. GBMs were
nearly blind to negative-price hours (F1 0.19 vs 0.57 for Timestral).

🚆 **Deutsche Bahn delays** (5 hub stations, 110 rolling origins): dead heat.
Best foundation model vs best gradient boosting: **0.07 minutes apart**. And on
the worst hour of the whole test (Frankfurt Hbf, 61 min average delay), every
model predicted under 8.

The fun part: **everything is replayable.** The Space lets you scrub through
every forecast origin, pick contenders, bet on which model wins, then reveal
what reality did.

- Zero-shot foundation models (Timestral 28M/209M, Chronos-2, TimesFM 3.0) vs
  retrained LightGBM/XGBoost vs seasonal-naive/climatology — all on CPU, no GPU
- Identical information at every origin; leakage guards by construction,
  protocols published as ADRs
- Follow the best forecast to schedule 4 MWh of daily load: −40 €/day, 74% of
  the perfect-foresight saving

🔗 Demo (replay any forecast): https://huggingface.co/spaces/Gjusev/forecast-arena
🔗 Code, data, full reports: https://github.com/Gjusev/forecast-arena

#time-series #forecasting #benchmark
