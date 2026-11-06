# LinkedIn Post 1 — Train delays (draft, DO NOT PUBLISH without approval)

---

I asked eight forecasting models to predict German train delays one hour
ahead. A 209-million-parameter foundation model won.

By 0.07 minutes.

Here's what we found. Deutsche Bahn delay data is public — 5.7 million
arrivals across Germany's five biggest stations, 2024–2026. We built a
benchmark that is honest by construction: models only ever see fully
completed hours. Nothing that wasn't knowable at prediction time.

The contenders:
→ 4 zero-shot foundation models (Mistral Timestral 28M & 209M, Amazon
Chronos-2, Google TimesFM 3.0) — no training, just inference
→ LightGBM & XGBoost with lag features, retrained per forecast
→ Seasonal naive ("tomorrow = yesterday") and hour-of-week averages

Results, 1 hour ahead, average arrival delay in minutes (lower = better):

Seasonal naive ........... 2.76
LightGBM ................. 1.92
Timestral 209M ........... 1.84

Every serious model beats naive by 30–33%. Statistically bulletproof
(p < 1e-8). But the gap between a 28M zero-shot model and tuned gradient
boosting? 0.06 minutes. About 4 seconds of average delay.

And the cost side: TimesFM needed 3,400× more compute than naive for a
0.07-minute edge over the best GBM.

The uncomfortable part: on Feb 5, 2026, Frankfurt's average delay spiked past
60 minutes at midday. All eight models — foundation or not — predicted a flat
5–10 minute day. Disruption hours are exactly the hours that matter, and
precisely the hours nobody predicted. Detection recall for disruption hours:
13–50%.

The honest takeaway: foundation models are real forecasters — well
calibrated (80% intervals covered 74–82% of actuals), trivially deployable,
no training pipeline. But on messy operational data, a gradient-boosted tree
you can train on a laptop is still within seconds of them. Scale bought
almost nothing here: the 209M model beat its 28M sibling by 0.02 minutes.

Full methodology, predictions file, and reproduction commands (13 min of CPU
to re-run the whole benchmark): github.com/Gjusev/forecast-arena

*Data: piebro/deutsche-bahn-data (CC-BY-4.0). Completed-hour protocol —
models never see en-route information, so this is a lower bound on what a
real dispatch system could do.*

---

**Post-publishing checklist (for me, not the post):** attach the disruption-day
chart and the accuracy bar chart; verify the GitHub link resolves; schedule
morning CET weekday.
