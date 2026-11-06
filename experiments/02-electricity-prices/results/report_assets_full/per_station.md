# Per-series errors

| model                    | series_id             |   h |    n |      mae |     rmse |
|:-------------------------|:----------------------|----:|-----:|---------:|---------:|
| Timestral 209M           | day_ahead_price/DE-LU |   1 | 1408 |  4.93554 |  7.29745 |
| Timestral 28M            | day_ahead_price/DE-LU |   1 | 1408 |  5.00777 |  7.33588 |
| Chronos-2                | day_ahead_price/DE-LU |   1 | 1408 |  5.16404 |  7.6406  |
| LightGBM                 | day_ahead_price/DE-LU |   1 | 1408 |  5.18457 |  7.63279 |
| TimesFM 3.0              | day_ahead_price/DE-LU |   1 | 1408 |  5.20774 |  7.58492 |
| XGBoost                  | day_ahead_price/DE-LU |   1 | 1408 |  5.30741 |  7.79117 |
| Seasonal naive (24h)     | day_ahead_price/DE-LU |   1 | 1408 | 20.4141  | 30.7601  |
| Hour-of-week climatology | day_ahead_price/DE-LU |   1 | 1408 | 40.4769  | 51.7344  |