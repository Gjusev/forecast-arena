# Diebold-Mariano vs seasonal naive (|error| loss)

Negative statistic = fewer losses than the baseline. p-value from a HAC normal approximation; treat families of tests with a multiple-testing caveat (28 model-horizon tests here).

| model                    |   h |   dm_stat |     p_value | better_than_baseline   |
|:-------------------------|----:|----------:|------------:|:-----------------------|
| Timestral 209M           |   1 | -6.71854  | 1.83554e-11 | True                   |
| LightGBM                 |   1 | -6.42806  | 1.29246e-10 | True                   |
| Timestral 28M            |   1 | -6.37702  | 1.80564e-10 | True                   |
| XGBoost                  |   1 | -6.28146  | 3.35406e-10 | True                   |
| Chronos-2                |   1 | -6.0113   | 1.84041e-09 | True                   |
| TimesFM 3.0              |   1 | -5.9111   | 3.39828e-09 | True                   |
| Hour-of-week climatology |   1 |  4.22223  | 2.41899e-05 | False                  |
| TimesFM 3.0              |   3 | -7.30884  | 2.69452e-13 | True                   |
| Chronos-2                |   3 | -7.15668  | 8.26555e-13 | True                   |
| Timestral 209M           |   3 | -7.08182  | 1.42271e-12 | True                   |
| Timestral 28M            |   3 | -6.94148  | 3.88017e-12 | True                   |
| LightGBM                 |   3 | -6.04073  | 1.53417e-09 | True                   |
| XGBoost                  |   3 | -6.02776  | 1.66253e-09 | True                   |
| Hour-of-week climatology |   3 |  4.86052  | 1.17076e-06 | False                  |
| TimesFM 3.0              |   6 | -3.57979  | 0.000343865 | True                   |
| Chronos-2                |   6 | -3.45282  | 0.00055476  | True                   |
| Timestral 28M            |   6 | -3.37957  | 0.000726    | True                   |
| Timestral 209M           |   6 | -3.37597  | 0.000735553 | True                   |
| LightGBM                 |   6 | -3.2359   | 0.0012126   | True                   |
| XGBoost                  |   6 | -3.14575  | 0.00165663  | True                   |
| Hour-of-week climatology |   6 |  0.319225 | 0.749556    | False                  |
| LightGBM                 |  24 | -3.21693  | 0.0012957   | True                   |
| XGBoost                  |  24 | -3.01585  | 0.00256263  | True                   |
| Chronos-2                |  24 | -2.94521  | 0.00322733  | True                   |
| TimesFM 3.0              |  24 | -2.93084  | 0.00338045  | True                   |
| Timestral 209M           |  24 | -2.83693  | 0.00455502  | True                   |
| Timestral 28M            |  24 | -2.65938  | 0.00782844  | True                   |
| Hour-of-week climatology |  24 |  1.83797  | 0.0660671   | False                  |