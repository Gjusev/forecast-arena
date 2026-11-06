# LinkedIn Post 2 — Electricity prices (draft, DO NOT PUBLISH without approval)

---

Germany's electricity market sometimes pays you to consume. Can an AI model
see those hours coming?

We tested it. 1,408 days of the German day-ahead auction, forecast under
strict pre-auction rules: models only ever saw prices that were already
published before the daily auction closed. 1,793 negative-price delivery
hours in the window.

Four zero-shot foundation models (no training) vs LightGBM, XGBoost, and
classical baselines.

Price accuracy (MAE, €/MWh — lower is better):

Seasonal naive ........... 28.20
LightGBM ................. 24.14
Chronos-2 ................ 19.27

Foundation models beat naive by 31–33%. But the bigger story: they beat the
GBMs by ~4.5 €/MWh. On train delays, trees matched them. On a wild,
nonstationary market — energy crisis one year, renewables collapsing prices
the next — zero-shot transfer won.

And the negative hours specifically:

→ Best negative-price detection: F1 0.57 (Timestral 209M)
→ The GBMs were nearly blind to negatives (F1 0.19–0.23) — they almost never
  predict below zero
→ All models are conservative: ~70% precision, ~40% recall. When they say
  "negative hour", they're usually right. They miss half of them.

Then the money question: does forecast quality translate into savings? We
simulated a consumer with 4 MWh of flexible load per day, placed in the
predicted-cheapest 4 hours, paid at real auction prices. 1,402 days:

Fixed midday schedule ...... 236.7 €/day
Model-scheduled ............ 196.6 €/day  (−17%)
Oracle (perfect foresight) . 182.8 €/day

The model captures 74% of what perfect foresight would give. Not bad for an
out-of-the-box model running on a CPU.

Honest caveats: this is wholesale market cost, not your household bill
(taxes, levies and grid fees dominate retail prices). And the spike
threshold we pre-registered on crisis-era training data turned out to flag
zero hours in the test window — we report the null instead of quietly
re-tuning.

Code, predictions file, and 13-minute reproduction:

github.com/Gjusev/forecast-arena

*Data: SMARD (Bundesnetzagentur, dl-de/by-2.0). Pre-auction protocol — no
model ever saw a price before it was published.*

---

**Attachments:** scheduling_cost_linkedin.png (1080×1350), negative-price day
chart.
