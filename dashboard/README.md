---
title: Forecast Arena
emoji: ⚡
colorFrom: yellow
colorTo: gray
sdk: gradio
sdk_version: "5.50.0"
app_file: app.py
pinned: true
license: mit
short_description: Replay, rank and duel AI vs classical forecasts on real data
---

# forecast-arena dashboard

Cached benchmark results from
[github.com/Gjusev/forecast-arena](https://github.com/Gjusev/forecast-arena):
time series foundation models vs traditional methods on Deutsche Bahn train
delays and German day-ahead electricity prices.

No live model inference happens here — every number traces to a committed
predictions file in the repository.
