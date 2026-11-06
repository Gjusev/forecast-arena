# LinkedIn Post 3 — Cross-experiment findings (draft, DO NOT PUBLISH without approval)

---

I benchmarked the same eight forecasting models on two completely different
real-world problems. The ranking flipped.

Problem 1: German train delays (5 hub stations, 110 rolling origins, 5.7M
arrivals, completed-hour protocol).

Problem 2: German day-ahead electricity prices (1,408 daily origins,
pre-auction protocol, 2021–2026).

Same models: Mistral Timestral 28M & 209M, Amazon Chronos-2, Google TimesFM
3.0 — all zero-shot — plus LightGBM, XGBoost, seasonal naive.

On trains, everyone serious beat naive by ~30%... and the gap between
foundation models and laptop-trained gradient boosting was 0.07 minutes.
Statistically significant, operationally irrelevant.

On electricity, foundation models beat naive by 31–33% and the GBMs by
~19%. Same models, same careful protocol — different data, different winner.

Three lessons after running both:

1. **"Which model is best" is the wrong question.** "Best on which data
   regime" is the right one. Stationary-ish, strongly seasonal → trees are
   enough. Structural shifts, skewed distributions, negative values →
   zero-shot foundation models transferred where trees regressed to the mean
   (they were nearly blind to negative prices).

2. **Well-calibrated uncertainty comes free with the foundation models.**
   Nominal 80% intervals covered 74–82% of actuals in BOTH experiments,
   out of the box. The naive baseline's residual intervals collapsed to 0.63
   coverage on prices. If you make decisions under uncertainty, that gap is
   worth more than a few MAE points.

3. **The expensive model is rarely worth it here.** TimesFM cost 3,400× the
   naive baseline's compute on trains and 528 seconds on electricity — and
   finished mid-pack. Timestral 28M (111 MB) matched or beat models 4–8×
   its size on both problems. For operational forecasting, small
   zero-shot models are the sweet spot.

And the finding I find most honest: on the worst disruption day in the train
data (60+ min average delay), every single model — foundation or not —
predicted a calm day. Benchmarks average away exactly the hours that matter.
Average skill scores are necessary, but read the failure analysis before you
deploy anything.

Everything reproducible: github.com/Gjusev/forecast-arena
Two technical reports, pre-registered thresholds, prediction files for every
claim, one command to re-run each benchmark.

*Delays data: piebro/deutsche-bahn-data (CC-BY-4.0). Prices: SMARD
(Bundesnetzagentur). CPU-only runs.*
