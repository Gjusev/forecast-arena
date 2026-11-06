# Headline metrics

| target        | model                    |   h |   n |     mae |    rmse |   skill_vs_baseline_pct |   coverage_80 |
|:--------------|:-------------------------|----:|----:|--------:|--------:|------------------------:|--------------:|
| avg_delay_min | Timestral 209M           |   1 | 550 | 1.84475 | 3.92564 |                33.2105  |      0.775735 |
| avg_delay_min | Timestral 28M            |   1 | 550 | 1.86695 | 3.97501 |                32.4069  |      0.766544 |
| avg_delay_min | Chronos-2                |   1 | 550 | 1.89416 | 4.1409  |                31.4216  |      0.759191 |
| avg_delay_min | TimesFM 3.0              |   1 | 550 | 1.89561 | 4.14668 |                31.3691  |      0.790441 |
| avg_delay_min | LightGBM                 |   1 | 550 | 1.91514 | 3.90639 |                30.662   |    nan        |
| avg_delay_min | XGBoost                  |   1 | 550 | 1.92772 | 3.91841 |                30.2068  |    nan        |
| avg_delay_min | Seasonal naive (24h)     |   1 | 550 | 2.76204 | 4.28809 |                 0       |      0.727941 |
| avg_delay_min | Hour-of-week climatology |   1 | 550 | 3.72525 | 6.07371 |               -34.8731  |    nan        |
| avg_delay_min | Timestral 209M           |   3 | 550 | 2.20184 | 4.45311 |                29.5698  |      0.818015 |
| avg_delay_min | TimesFM 3.0              |   3 | 550 | 2.22259 | 4.47836 |                28.9062  |      0.784926 |
| avg_delay_min | Chronos-2                |   3 | 550 | 2.22403 | 4.50563 |                28.8601  |      0.788603 |
| avg_delay_min | Timestral 28M            |   3 | 550 | 2.24168 | 4.46116 |                28.2957  |      0.814338 |
| avg_delay_min | LightGBM                 |   3 | 550 | 2.35373 | 4.56507 |                24.7115  |    nan        |
| avg_delay_min | XGBoost                  |   3 | 550 | 2.36146 | 4.55992 |                24.4642  |    nan        |
| avg_delay_min | Seasonal naive (24h)     |   3 | 550 | 3.12628 | 5.6821  |                 0       |      0.700368 |
| avg_delay_min | Hour-of-week climatology |   3 | 550 | 4.41893 | 6.6793  |               -41.3479  |    nan        |
| avg_delay_min | TimesFM 3.0              |   6 | 550 | 2.3093  | 5.07106 |                39.0916  |      0.789179 |
| avg_delay_min | Chronos-2                |   6 | 550 | 2.35716 | 5.14113 |                37.8294  |      0.764925 |
| avg_delay_min | Timestral 209M           |   6 | 550 | 2.37946 | 5.2238  |                37.2411  |      0.807836 |
| avg_delay_min | Timestral 28M            |   6 | 550 | 2.39519 | 5.18579 |                36.8263  |      0.796642 |
| avg_delay_min | LightGBM                 |   6 | 550 | 2.57857 | 5.25681 |                31.9896  |    nan        |
| avg_delay_min | XGBoost                  |   6 | 550 | 2.58407 | 5.23376 |                31.8444  |    nan        |
| avg_delay_min | Seasonal naive (24h)     |   6 | 550 | 3.79143 | 9.11838 |                 0       |      0.708955 |
| avg_delay_min | Hour-of-week climatology |   6 | 550 | 3.95717 | 7.58283 |                -4.37131 |    nan        |
| avg_delay_min | Chronos-2                |  24 | 550 | 2.08419 | 3.80182 |                23.0108  |      0.765996 |
| avg_delay_min | TimesFM 3.0              |  24 | 550 | 2.09564 | 3.79686 |                22.5879  |      0.798903 |
| avg_delay_min | LightGBM                 |  24 | 550 | 2.10075 | 3.25181 |                22.3992  |    nan        |
| avg_delay_min | Timestral 209M           |  24 | 550 | 2.10584 | 3.85141 |                22.2112  |      0.819013 |
| avg_delay_min | XGBoost                  |  24 | 550 | 2.12935 | 3.39446 |                21.3426  |    nan        |
| avg_delay_min | Timestral 28M            |  24 | 550 | 2.14037 | 3.87614 |                20.9355  |      0.8117   |
| avg_delay_min | Seasonal naive (24h)     |  24 | 550 | 2.70712 | 4.69936 |                 0       |      0.736746 |
| avg_delay_min | Hour-of-week climatology |  24 | 550 | 3.16687 | 4.82177 |               -16.9831  |    nan        |