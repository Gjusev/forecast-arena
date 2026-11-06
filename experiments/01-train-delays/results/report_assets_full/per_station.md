# Per-series errors

| model                    | series_id                        |   h |   n |      mae |     rmse |
|:-------------------------|:---------------------------------|----:|----:|---------:|---------:|
| Timestral 28M            | avg_delay_min/Berlin Hbf         |   1 | 110 |  1.22702 |  1.65546 |
| Timestral 209M           | avg_delay_min/Berlin Hbf         |   1 | 110 |  1.22757 |  1.68158 |
| Chronos-2                | avg_delay_min/Berlin Hbf         |   1 | 110 |  1.257   |  1.84729 |
| TimesFM 3.0              | avg_delay_min/Berlin Hbf         |   1 | 110 |  1.26188 |  1.78782 |
| LightGBM                 | avg_delay_min/Berlin Hbf         |   1 | 110 |  1.32973 |  1.62402 |
| XGBoost                  | avg_delay_min/Berlin Hbf         |   1 | 110 |  1.37742 |  1.7047  |
| Seasonal naive (24h)     | avg_delay_min/Berlin Hbf         |   1 | 110 |  1.88097 |  2.65098 |
| Hour-of-week climatology | avg_delay_min/Berlin Hbf         |   1 | 110 |  3.06044 |  4.77606 |
| Chronos-2                | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  2.06844 |  6.04113 |
| TimesFM 3.0              | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  2.0945  |  5.99097 |
| Timestral 209M           | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  2.10053 |  6.00836 |
| LightGBM                 | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  2.12648 |  5.57801 |
| Timestral 28M            | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  2.14411 |  6.03578 |
| XGBoost                  | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  2.15345 |  5.62822 |
| Seasonal naive (24h)     | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  3.02439 |  4.55312 |
| Hour-of-week climatology | avg_delay_min/Frankfurt(Main)Hbf |   1 | 110 |  4.02131 |  6.69487 |
| Timestral 209M           | avg_delay_min/Hamburg Hbf        |   1 | 110 |  1.48582 |  3.03129 |
| Timestral 28M            | avg_delay_min/Hamburg Hbf        |   1 | 110 |  1.52043 |  3.02818 |
| TimesFM 3.0              | avg_delay_min/Hamburg Hbf        |   1 | 110 |  1.55173 |  3.14459 |
| LightGBM                 | avg_delay_min/Hamburg Hbf        |   1 | 110 |  1.59099 |  3.04248 |
| XGBoost                  | avg_delay_min/Hamburg Hbf        |   1 | 110 |  1.62522 |  3.07358 |
| Chronos-2                | avg_delay_min/Hamburg Hbf        |   1 | 110 |  1.64078 |  3.43342 |
| Seasonal naive (24h)     | avg_delay_min/Hamburg Hbf        |   1 | 110 |  2.19898 |  3.81774 |
| Hour-of-week climatology | avg_delay_min/Hamburg Hbf        |   1 | 110 |  3.09668 |  5.32263 |
| Timestral 28M            | avg_delay_min/Köln Hbf           |   1 | 110 |  2.84702 |  5.15172 |
| Timestral 209M           | avg_delay_min/Köln Hbf           |   1 | 110 |  2.85342 |  4.99332 |
| Chronos-2                | avg_delay_min/Köln Hbf           |   1 | 110 |  2.97548 |  5.49271 |
| TimesFM 3.0              | avg_delay_min/Köln Hbf           |   1 | 110 |  2.98294 |  5.72676 |
| XGBoost                  | avg_delay_min/Köln Hbf           |   1 | 110 |  3.01694 |  5.3954  |
| LightGBM                 | avg_delay_min/Köln Hbf           |   1 | 110 |  3.06807 |  5.45136 |
| Seasonal naive (24h)     | avg_delay_min/Köln Hbf           |   1 | 110 |  3.75787 |  5.60787 |
| Hour-of-week climatology | avg_delay_min/Köln Hbf           |   1 | 110 |  4.92406 |  7.1869  |
| LightGBM                 | avg_delay_min/München Hbf        |   1 | 110 |  1.44038 |  1.78497 |
| XGBoost                  | avg_delay_min/München Hbf        |   1 | 110 |  1.44679 |  1.80214 |
| Chronos-2                | avg_delay_min/München Hbf        |   1 | 110 |  1.5118  |  1.87101 |
| Timestral 209M           | avg_delay_min/München Hbf        |   1 | 110 |  1.5345  |  1.89894 |
| TimesFM 3.0              | avg_delay_min/München Hbf        |   1 | 110 |  1.56561 |  1.93476 |
| Timestral 28M            | avg_delay_min/München Hbf        |   1 | 110 |  1.5746  |  1.92406 |
| Seasonal naive (24h)     | avg_delay_min/München Hbf        |   1 | 110 |  2.91439 |  4.22847 |
| Hour-of-week climatology | avg_delay_min/München Hbf        |   1 | 110 |  3.48913 |  6.02652 |
| LightGBM                 | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  2.72999 |  3.70983 |
| XGBoost                  | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  2.79769 |  3.77162 |
| Chronos-2                | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  2.83342 |  3.92411 |
| Timestral 28M            | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  2.84944 |  3.9757  |
| Timestral 209M           | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  2.86708 |  3.97996 |
| TimesFM 3.0              | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  2.98535 |  4.02431 |
| Seasonal naive (24h)     | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  4.37911 |  6.0964  |
| Hour-of-week climatology | n_delayed_gt5/Berlin Hbf         |   1 | 110 |  8.49444 | 10.0889  |
| XGBoost                  | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 |  4.88458 |  6.90215 |
| Chronos-2                | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 |  4.92186 |  6.98282 |
| LightGBM                 | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 |  4.96069 |  6.98269 |
| TimesFM 3.0              | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 |  4.96393 |  7.13319 |
| Timestral 28M            | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 |  5.12931 |  7.29799 |
| Timestral 209M           | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 |  5.16123 |  7.32407 |
| Seasonal naive (24h)     | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 |  8       | 10.7221  |
| Hour-of-week climatology | n_delayed_gt5/Frankfurt(Main)Hbf |   1 | 110 | 14.397   | 17.7606  |
| Timestral 28M            | n_delayed_gt5/Hamburg Hbf        |   1 | 110 |  4.17809 |  7.2185  |
| Timestral 209M           | n_delayed_gt5/Hamburg Hbf        |   1 | 110 |  4.24198 |  7.17844 |
| TimesFM 3.0              | n_delayed_gt5/Hamburg Hbf        |   1 | 110 |  4.2912  |  7.27629 |
| XGBoost                  | n_delayed_gt5/Hamburg Hbf        |   1 | 110 |  4.45715 |  6.87978 |
| Chronos-2                | n_delayed_gt5/Hamburg Hbf        |   1 | 110 |  4.50193 |  7.31358 |
| LightGBM                 | n_delayed_gt5/Hamburg Hbf        |   1 | 110 |  4.51799 |  6.93938 |
| Seasonal naive (24h)     | n_delayed_gt5/Hamburg Hbf        |   1 | 110 |  8.32143 | 12.8358  |
| Hour-of-week climatology | n_delayed_gt5/Hamburg Hbf        |   1 | 110 | 10.967   | 14.2283  |
| Chronos-2                | n_delayed_gt5/Köln Hbf           |   1 | 110 |  3.89635 |  5.27348 |
| XGBoost                  | n_delayed_gt5/Köln Hbf           |   1 | 110 |  3.90207 |  5.42969 |
| LightGBM                 | n_delayed_gt5/Köln Hbf           |   1 | 110 |  3.90732 |  5.38786 |
| TimesFM 3.0              | n_delayed_gt5/Köln Hbf           |   1 | 110 |  3.92579 |  5.23141 |
| Timestral 209M           | n_delayed_gt5/Köln Hbf           |   1 | 110 |  3.93738 |  5.29697 |
| Timestral 28M            | n_delayed_gt5/Köln Hbf           |   1 | 110 |  4.02495 |  5.38651 |
| Seasonal naive (24h)     | n_delayed_gt5/Köln Hbf           |   1 | 110 |  5.61818 |  7.33857 |
| Hour-of-week climatology | n_delayed_gt5/Köln Hbf           |   1 | 110 | 12.235   | 14.6531  |
| XGBoost                  | n_delayed_gt5/München Hbf        |   1 | 110 |  4.82653 |  6.55684 |
| Timestral 209M           | n_delayed_gt5/München Hbf        |   1 | 110 |  4.88031 |  6.81806 |
| TimesFM 3.0              | n_delayed_gt5/München Hbf        |   1 | 110 |  4.90084 |  6.67712 |
| Timestral 28M            | n_delayed_gt5/München Hbf        |   1 | 110 |  4.91668 |  6.72984 |
| LightGBM                 | n_delayed_gt5/München Hbf        |   1 | 110 |  5.03087 |  6.728   |
| Chronos-2                | n_delayed_gt5/München Hbf        |   1 | 110 |  5.11896 |  7.02808 |
| Seasonal naive (24h)     | n_delayed_gt5/München Hbf        |   1 | 110 | 10.0909  | 14.7728  |
| Hour-of-week climatology | n_delayed_gt5/München Hbf        |   1 | 110 | 14.2605  | 17.5292  |