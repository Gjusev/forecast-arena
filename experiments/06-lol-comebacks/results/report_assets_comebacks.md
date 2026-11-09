# Comeback anticipation (experiment 06)

Tier: **full**. Pre-registered rule: comeback-eligible = gold_diff at minute 15 <= -2000 (blue behind by 2000+ gold). Reality flip = gold_diff >= 0 at any game-minute 16..35. A model predicts a comeback when its point forecast crosses 0 at any h <= 20.

Of **383** eligible matches, **199** actually flipped (base rate 52.0%). Most common patch among analysed matches: 13.24.547.9214 (78 of 1419, 5%).

| model | predicted | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| drift | 9 | 5 | 4 | 194 | 0.556 | 0.025 | 0.048 |
| timesfm_3_0 | 23 | 14 | 9 | 185 | 0.609 | 0.07 | 0.126 |
| chronos_2 | 21 | 12 | 9 | 187 | 0.571 | 0.06 | 0.109 |
| persistence | 1 | 0 | 1 | 199 | 0.0 | 0.0 | 0.0 |
| timestral_28M | 11 | 6 | 5 | 193 | 0.545 | 0.03 | 0.057 |
| timestral_209M | 9 | 5 | 4 | 194 | 0.556 | 0.025 | 0.048 |

In plain language: we keep only the matches where one side was clearly behind at minute 15 (at least 2,000 gold down), and ask which models said - within their next-20-minute forecast - that the trailing side would pull level (forecast crossing 0). Precision is how often that call was right; recall is how many real turnarounds it caught. Because a share of matches flip anyway, a constant 'always comeback' call would score precision 0.520 at recall 1.0, so a model only earns credit above that line.

Honesty notes:
- ranked matches only (queues 420/440): ARAM and Arena gold curves are excluded as a different process
- matches from the same patch share meta; rows are correlated, not independent samples
- 60 s frame resolution: leads that flip and re-flip inside a minute are invisible
