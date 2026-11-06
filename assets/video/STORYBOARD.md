# forecast-arena — motion piece storyboard

Concept: **the origin line.** Every forecast in this benchmark starts at a
vertical line in time: left of it is known, right of it is guessed, and then
reality arrives. The film is that moment, across four arenas. A yellow origin
bar (German high-voltage-sign yellow: "AI") sweeps between scenes as the only
transition; reality is always drawn in paper white.

Brief (blank-page house shape):

```
in forecast-arena, assets/video/src/index.html, new comp story, create the following, in high-voltage signage on black (ink #0b0b0b, paper #f3f1ea, signal #ffd400, model families blue/orange/aqua), using deterministic svg frames rendered by playwright + ffmpeg:

1. a paper history line runs in from the left; at ~1s the yellow origin bar drops; "AI vs Reality" rises word by word above it
2. trains, frankfurt hbf 5 feb 2026 02:00: six model forecasts fan out right of the origin bar, all under 8 min
3. the turn: reality's first hour lands at 61 min, the y axis zooms out 12 -> 70 and every forecast collapses to the floor
4. the leaderboard races in: 550 forecasts, foundation vs gradient boosting 0.07 min apart
5. power, sunday 7 jul 2024: forecasts dip below zero a day early, reality follows, 17 negative hours fill in yellow
6. the power leaderboard: foundation +33% vs gradient boosting +19%
7. weather, 30 german cities, a day ahead: skill bars from a zero axis — AI holds +6.5%, XGBoost sinks to -7.7% below 'yesterday'
8. renewables, 4 feb 2023: naive expects 42 GW dying, reality ramps to 12 GW, AI tracks it; +93% at 1h, +11% vs +5% a day ahead
9. money: 4 MWh a day moved to the forecast-cheapest hours, -40.2 €/day, 74% of perfect foresight
10. end card: the logo mark draws itself, urls

camera stays still; every scene change is the origin bar sweeping left to right, ease-in-out, 0.6s
1920x1080, 30fps, ~44.5s, no audio; every number from assets/video/story.json
```

| # | time (s) | scene | on screen | data source |
|---|---|---|---|---|
| 1 | 0.0–3.6 | Cold open | history line, origin bar drop, title | prices actual (shape only) |
| 2 | 3.6–10.4 | Trains: the miss | 6 forecasts → reality 61 min → y-axis zoom-out | `delays` |
| 3 | 10.4–14.8 | Trains: dead heat | MAE bars, "0.07 min" | `leader_delays` |
| 4 | 14.8–21.0 | Power: the catch | forecasts below zero, reality, 17 h shaded | `prices` |
| 5 | 21.0–25.2 | Power: FMs win | skill bars, neg-price F1 | `leader_prices`, `neg_f1` |
| 6 | 25.2–30.4 | Weather: a day ahead | skill bars from a zero axis, XGBoost at −7.7% | `weather24` |
| 7 | 30.4–36.2 | Renewables: the ramp | naive vs AI vs reality, wind day 4 Feb 2023 | `renew` |
| 8 | 36.2–40.6 | Money | fixed vs model vs oracle €/day | `scheduling` |
| 9 | 40.6–44.5 | End card | mark draw, wordmark, URLs | — |

Honesty notes: scene 2 is the worst disruption hour in the window (same rule as
`scripts/make_charts.py`); scene 4 is an illustrative solar Sunday chosen for
clarity, so scene 5 shows the aggregate F1 (~0.5) right after it; scene 7 picks
the day with the largest naive-vs-AI gap on wind_total, so scene 7 also carries
the aggregate +11%/+5% skills alongside the single-day story.

Render: `uv run --with playwright python scripts/render_motion.py`
(needs Chrome + ffmpeg). Outputs `forecast-arena.mp4`, `preview.gif`,
`stills/*.png` and the brand PNGs.
