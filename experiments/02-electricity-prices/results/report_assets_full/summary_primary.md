# Headline metrics

| target          | model                    |   h |    n |      mae |     rmse |   skill_vs_baseline_pct |   coverage_80 |
|:----------------|:-------------------------|----:|-----:|---------:|---------:|------------------------:|--------------:|
| day_ahead_price | Timestral 209M           |   1 | 1408 |  4.93554 |  7.29745 |               75.8228   |      0.722617 |
| day_ahead_price | Timestral 28M            |   1 | 1408 |  5.00777 |  7.33588 |               75.469    |      0.772404 |
| day_ahead_price | Chronos-2                |   1 | 1408 |  5.16404 |  7.6406  |               74.7035   |      0.752489 |
| day_ahead_price | LightGBM                 |   1 | 1408 |  5.18457 |  7.63279 |               74.6029   |    nan        |
| day_ahead_price | TimesFM 3.0              |   1 | 1408 |  5.20774 |  7.58492 |               74.4894   |      0.715505 |
| day_ahead_price | XGBoost                  |   1 | 1408 |  5.30741 |  7.79117 |               74.0012   |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   1 | 1408 | 20.4141  | 30.7601  |                0        |      0.709815 |
| day_ahead_price | Hour-of-week climatology |   1 | 1408 | 40.4769  | 51.7344  |              -98.2797   |    nan        |
| day_ahead_price | Timestral 209M           |   2 | 1408 |  5.91781 |  8.67726 |               70.6247   |      0.82311  |
| day_ahead_price | Timestral 28M            |   2 | 1408 |  5.95054 |  8.69147 |               70.4623   |      0.840942 |
| day_ahead_price | Chronos-2                |   2 | 1408 |  6.08687 |  8.95719 |               69.7855   |      0.794579 |
| day_ahead_price | TimesFM 3.0              |   2 | 1408 |  6.50485 |  9.41265 |               67.7107   |      0.773181 |
| day_ahead_price | LightGBM                 |   2 | 1408 |  6.8068  |  9.59146 |               66.2119   |    nan        |
| day_ahead_price | XGBoost                  |   2 | 1408 |  6.91192 |  9.82772 |               65.6901   |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   2 | 1408 | 20.1455  | 30.7045  |                0        |      0.716833 |
| day_ahead_price | Hour-of-week climatology |   2 | 1408 | 46.5733  | 59.2989  |             -131.184    |    nan        |
| day_ahead_price | Timestral 209M           |   3 | 1408 |  7.0881  | 10.4694  |               64.8091   |      0.842817 |
| day_ahead_price | Timestral 28M            |   3 | 1408 |  7.13382 | 10.5002  |               64.5821   |      0.866287 |
| day_ahead_price | Chronos-2                |   3 | 1408 |  7.34557 | 10.8599  |               63.5308   |      0.800853 |
| day_ahead_price | TimesFM 3.0              |   3 | 1408 |  7.76435 | 11.3679  |               61.4516   |      0.814367 |
| day_ahead_price | LightGBM                 |   3 | 1408 |  8.36655 | 11.7186  |               58.4618   |    nan        |
| day_ahead_price | XGBoost                  |   3 | 1408 |  8.53388 | 12.3451  |               57.631    |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   3 | 1408 | 20.1418  | 30.797   |                0        |      0.714794 |
| day_ahead_price | Hour-of-week climatology |   3 | 1408 | 51.1114  | 65.8414  |             -153.758    |    nan        |
| day_ahead_price | Timestral 28M            |   4 | 1408 |  7.96775 | 11.8669  |               60.2975   |      0.874822 |
| day_ahead_price | Timestral 209M           |   4 | 1408 |  8.00506 | 11.866   |               60.1116   |      0.852063 |
| day_ahead_price | Chronos-2                |   4 | 1408 |  8.24061 | 12.2549  |               58.9379   |      0.802987 |
| day_ahead_price | TimesFM 3.0              |   4 | 1408 |  8.67421 | 12.8161  |               56.7773   |      0.858464 |
| day_ahead_price | LightGBM                 |   4 | 1408 |  9.7385  | 13.6737  |               51.4741   |    nan        |
| day_ahead_price | XGBoost                  |   4 | 1408 |  9.93711 | 15.141   |               50.4844   |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   4 | 1408 | 20.0686  | 30.674   |                0        |      0.71266  |
| day_ahead_price | Hour-of-week climatology |   4 | 1408 | 51.6681  | 66.5349  |             -157.457    |    nan        |
| day_ahead_price | Timestral 28M            |   5 | 1408 |  9.47654 | 13.9544  |               53.589    |      0.866287 |
| day_ahead_price | Timestral 209M           |   5 | 1408 |  9.50647 | 13.9903  |               53.4424   |      0.836415 |
| day_ahead_price | Chronos-2                |   5 | 1408 |  9.60887 | 14.1238  |               52.941    |      0.803698 |
| day_ahead_price | TimesFM 3.0              |   5 | 1408 | 10.1117  | 14.7109  |               50.4784   |      0.868421 |
| day_ahead_price | LightGBM                 |   5 | 1408 | 11.2496  | 15.7706  |               44.9054   |    nan        |
| day_ahead_price | XGBoost                  |   5 | 1408 | 11.7132  | 19.3855  |               42.635    |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   5 | 1408 | 20.4188  | 30.9839  |                0        |      0.694879 |
| day_ahead_price | Hour-of-week climatology |   5 | 1408 | 50.7145  | 64.3844  |             -148.372    |    nan        |
| day_ahead_price | Chronos-2                |   6 | 1408 | 12.5269  | 17.7594  |               48.9468   |      0.777383 |
| day_ahead_price | Timestral 209M           |   6 | 1408 | 13.2273  | 18.6149  |               46.0927   |      0.790185 |
| day_ahead_price | TimesFM 3.0              |   6 | 1408 | 13.3757  | 18.6944  |               45.4878   |      0.825036 |
| day_ahead_price | Timestral 28M            |   6 | 1408 | 13.7741  | 19.1747  |               43.864    |      0.789474 |
| day_ahead_price | LightGBM                 |   6 | 1408 | 14.1057  | 19.8978  |               42.5126   |    nan        |
| day_ahead_price | XGBoost                  |   6 | 1408 | 14.5277  | 22.9011  |               40.793    |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   6 | 1408 | 24.537   | 35.669   |                0        |      0.640825 |
| day_ahead_price | Hour-of-week climatology |   6 | 1408 | 52.8088  | 66.149   |             -115.221    |    nan        |
| day_ahead_price | Chronos-2                |   7 | 1408 | 16.8522  | 24.0556  |               46.2266   |      0.731863 |
| day_ahead_price | TimesFM 3.0              |   7 | 1408 | 18.209   | 25.6901  |               41.8972   |      0.785917 |
| day_ahead_price | Timestral 209M           |   7 | 1408 | 18.7019  | 26.189   |               40.3245   |      0.721195 |
| day_ahead_price | XGBoost                  |   7 | 1408 | 19.0254  | 27.8598  |               39.2925   |    nan        |
| day_ahead_price | LightGBM                 |   7 | 1408 | 19.3048  | 27.0902  |               38.4008   |    nan        |
| day_ahead_price | Timestral 28M            |   7 | 1408 | 19.6669  | 27.0862  |               37.2453   |      0.717639 |
| day_ahead_price | Seasonal naive (24h)     |   7 | 1408 | 31.3394  | 44.7452  |                0        |      0.592461 |
| day_ahead_price | Hour-of-week climatology |   7 | 1408 | 50.5302  | 64.587   |              -61.2354   |    nan        |
| day_ahead_price | Chronos-2                |   8 | 1408 | 18.9176  | 29.666   |               45.1458   |      0.746799 |
| day_ahead_price | TimesFM 3.0              |   8 | 1408 | 20.4158  | 30.6573  |               40.8015   |      0.778094 |
| day_ahead_price | Timestral 209M           |   8 | 1408 | 21.0681  | 30.9325  |               38.9101   |      0.750356 |
| day_ahead_price | XGBoost                  |   8 | 1408 | 21.8912  | 32.99    |               36.5232   |    nan        |
| day_ahead_price | Timestral 28M            |   8 | 1408 | 22.3233  | 31.7792  |               35.2703   |      0.709815 |
| day_ahead_price | LightGBM                 |   8 | 1408 | 22.5482  | 32.5759  |               34.6183   |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   8 | 1408 | 34.487   | 49.3638  |                0        |      0.566856 |
| day_ahead_price | Hour-of-week climatology |   8 | 1408 | 38.3719  | 52.0629  |              -11.2648   |    nan        |
| day_ahead_price | Chronos-2                |   9 | 1408 | 19.9582  | 31.5587  |               42.3594   |      0.748222 |
| day_ahead_price | Timestral 209M           |   9 | 1408 | 21.5741  | 32.7079  |               37.6928   |      0.77596  |
| day_ahead_price | TimesFM 3.0              |   9 | 1408 | 21.5781  | 33.5599  |               37.681    |      0.789474 |
| day_ahead_price | Timestral 28M            |   9 | 1408 | 22.7738  | 33.1895  |               34.2278   |      0.733286 |
| day_ahead_price | XGBoost                  |   9 | 1408 | 24.6983  | 37.0466  |               28.6698   |    nan        |
| day_ahead_price | LightGBM                 |   9 | 1408 | 25.6199  | 37.3025  |               26.0081   |    nan        |
| day_ahead_price | Seasonal naive (24h)     |   9 | 1408 | 34.6253  | 49.5792  |                0        |      0.561878 |
| day_ahead_price | Hour-of-week climatology |   9 | 1408 | 38.827   | 52.2237  |              -12.1347   |    nan        |
| day_ahead_price | Chronos-2                |  10 | 1408 | 20.9442  | 31.8883  |               35.2593   |      0.759602 |
| day_ahead_price | Timestral 209M           |  10 | 1408 | 22.0086  | 32.7374  |               31.9692   |      0.800853 |
| day_ahead_price | TimesFM 3.0              |  10 | 1408 | 22.4678  | 33.3211  |               30.5496   |      0.792319 |
| day_ahead_price | Timestral 28M            |  10 | 1408 | 22.7168  | 32.7401  |               29.78     |      0.751067 |
| day_ahead_price | XGBoost                  |  10 | 1408 | 28.2041  | 40.0808  |               12.8184   |    nan        |
| day_ahead_price | LightGBM                 |  10 | 1408 | 29.4281  | 40.9904  |                9.03482  |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  10 | 1408 | 32.3509  | 46.0792  |                0        |      0.576102 |
| day_ahead_price | Hour-of-week climatology |  10 | 1408 | 51.319   | 64.9817  |              -58.6324   |    nan        |
| day_ahead_price | Chronos-2                |  11 | 1408 | 22.6981  | 33.1433  |               28.3798   |      0.746799 |
| day_ahead_price | Timestral 209M           |  11 | 1408 | 23.4799  | 33.9667  |               25.9127   |      0.774538 |
| day_ahead_price | TimesFM 3.0              |  11 | 1408 | 23.7096  | 33.5822  |               25.1881   |      0.783073 |
| day_ahead_price | Timestral 28M            |  11 | 1408 | 23.9612  | 33.6499  |               24.3942   |      0.721906 |
| day_ahead_price | XGBoost                  |  11 | 1408 | 31.5589  | 43.7402  |                0.420732 |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  11 | 1408 | 31.6923  | 44.7371  |                0        |      0.572546 |
| day_ahead_price | LightGBM                 |  11 | 1408 | 33.3689  | 45.38    |               -5.29042  |    nan        |
| day_ahead_price | Hour-of-week climatology |  11 | 1408 | 54.1258  | 68.9637  |              -70.7855   |    nan        |
| day_ahead_price | Chronos-2                |  12 | 1408 | 24.277   | 36.1383  |               24.9219   |      0.743954 |
| day_ahead_price | Timestral 209M           |  12 | 1408 | 24.7809  | 36.4398  |               23.3636   |      0.752489 |
| day_ahead_price | TimesFM 3.0              |  12 | 1408 | 25.0596  | 36.113   |               22.5019   |      0.774538 |
| day_ahead_price | Timestral 28M            |  12 | 1408 | 25.0756  | 36.0499  |               22.4524   |      0.719772 |
| day_ahead_price | Seasonal naive (24h)     |  12 | 1408 | 32.3357  | 46.7148  |                0        |      0.583215 |
| day_ahead_price | XGBoost                  |  12 | 1408 | 33.9331  | 48.0449  |               -4.94002  |    nan        |
| day_ahead_price | LightGBM                 |  12 | 1408 | 36.0358  | 49.9664  |              -11.4429   |    nan        |
| day_ahead_price | Hour-of-week climatology |  12 | 1408 | 52.8107  | 69.3628  |              -63.3201   |    nan        |
| day_ahead_price | Chronos-2                |  13 | 1408 | 25.657   | 40.0926  |               23.9295   |      0.744666 |
| day_ahead_price | Timestral 209M           |  13 | 1408 | 26.0808  | 40.1663  |               22.673    |      0.743243 |
| day_ahead_price | Timestral 28M            |  13 | 1408 | 26.3434  | 39.7041  |               21.8943   |      0.692745 |
| day_ahead_price | TimesFM 3.0              |  13 | 1408 | 26.3821  | 39.86    |               21.7796   |      0.763158 |
| day_ahead_price | Seasonal naive (24h)     |  13 | 1408 | 33.7279  | 51.2801  |                0        |      0.578236 |
| day_ahead_price | XGBoost                  |  13 | 1408 | 34.797   | 51.4767  |               -3.16999  |    nan        |
| day_ahead_price | LightGBM                 |  13 | 1408 | 37.3157  | 53.7736  |              -10.6375   |    nan        |
| day_ahead_price | Hour-of-week climatology |  13 | 1408 | 54.4283  | 73.4112  |              -61.3747   |    nan        |
| day_ahead_price | Chronos-2                |  14 | 1408 | 26.2831  | 41.7184  |               22.9134   |      0.743954 |
| day_ahead_price | Timestral 209M           |  14 | 1408 | 26.6376  | 41.8701  |               21.8738   |      0.733286 |
| day_ahead_price | Timestral 28M            |  14 | 1408 | 26.9165  | 41.3306  |               21.0555   |      0.704125 |
| day_ahead_price | TimesFM 3.0              |  14 | 1408 | 26.9734  | 41.3831  |               20.8887   |      0.750356 |
| day_ahead_price | Seasonal naive (24h)     |  14 | 1408 | 34.0955  | 53.4541  |                0        |      0.578947 |
| day_ahead_price | XGBoost                  |  14 | 1408 | 34.5669  | 52.206   |               -1.38239  |    nan        |
| day_ahead_price | LightGBM                 |  14 | 1408 | 37.0301  | 54.075   |               -8.60693  |    nan        |
| day_ahead_price | Hour-of-week climatology |  14 | 1408 | 54.022   | 73.6923  |              -58.443    |    nan        |
| day_ahead_price | Chronos-2                |  15 | 1408 | 24.9193  | 37.3566  |               22.3801   |      0.761024 |
| day_ahead_price | Timestral 209M           |  15 | 1408 | 25.4089  | 37.6208  |               20.8549   |      0.737553 |
| day_ahead_price | Timestral 28M            |  15 | 1408 | 25.7238  | 37.1988  |               19.8743   |      0.72404  |
| day_ahead_price | TimesFM 3.0              |  15 | 1408 | 25.9329  | 37.5167  |               19.2227   |      0.770982 |
| day_ahead_price | Seasonal naive (24h)     |  15 | 1408 | 32.1043  | 47.6123  |                0        |      0.586771 |
| day_ahead_price | XGBoost                  |  15 | 1408 | 33.2064  | 46.7127  |               -3.43288  |    nan        |
| day_ahead_price | LightGBM                 |  15 | 1408 | 35.2944  | 48.678   |               -9.93677  |    nan        |
| day_ahead_price | Hour-of-week climatology |  15 | 1408 | 49.7113  | 66.4527  |              -54.8433   |    nan        |
| day_ahead_price | Chronos-2                |  16 | 1408 | 23.9744  | 36.2782  |               22.2979   |      0.766714 |
| day_ahead_price | Timestral 209M           |  16 | 1408 | 24.3867  | 36.2203  |               20.9615   |      0.770982 |
| day_ahead_price | Timestral 28M            |  16 | 1408 | 24.7688  | 36.1172  |               19.7231   |      0.763869 |
| day_ahead_price | TimesFM 3.0              |  16 | 1408 | 24.9334  | 36.651   |               19.1895   |      0.794452 |
| day_ahead_price | Seasonal naive (24h)     |  16 | 1408 | 30.8542  | 45.2587  |                0        |      0.605974 |
| day_ahead_price | XGBoost                  |  16 | 1408 | 31.3532  | 42.7852  |               -1.61723  |    nan        |
| day_ahead_price | LightGBM                 |  16 | 1408 | 32.6155  | 44.4863  |               -5.70851  |    nan        |
| day_ahead_price | Hour-of-week climatology |  16 | 1408 | 44.8682  | 60.4458  |              -45.4199   |    nan        |
| day_ahead_price | Timestral 209M           |  17 | 1408 | 24.5544  | 39.0202  |               20.0443   |      0.785206 |
| day_ahead_price | Timestral 28M            |  17 | 1408 | 24.5876  | 38.6706  |               19.9363   |      0.798009 |
| day_ahead_price | Chronos-2                |  17 | 1408 | 24.867   | 40.3805  |               19.0265   |      0.788051 |
| day_ahead_price | TimesFM 3.0              |  17 | 1408 | 24.9589  | 40.4878  |               18.7272   |      0.807255 |
| day_ahead_price | XGBoost                  |  17 | 1408 | 29.6471  | 43.5271  |                3.461    |    nan        |
| day_ahead_price | LightGBM                 |  17 | 1408 | 30.3036  | 44.6299  |                1.32333  |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  17 | 1408 | 30.71    | 47.8753  |                0        |      0.610953 |
| day_ahead_price | Hour-of-week climatology |  17 | 1408 | 40.3445  | 59.1974  |              -31.3723   |    nan        |
| day_ahead_price | Timestral 209M           |  18 | 1408 | 26.0501  | 46.8537  |               20.3052   |      0.79872  |
| day_ahead_price | Timestral 28M            |  18 | 1408 | 26.2676  | 46.5917  |               19.6399   |      0.825747 |
| day_ahead_price | Chronos-2                |  18 | 1408 | 26.4821  | 48.21    |               18.9837   |      0.805121 |
| day_ahead_price | TimesFM 3.0              |  18 | 1408 | 26.5316  | 49.0534  |               18.8322   |      0.825747 |
| day_ahead_price | XGBoost                  |  18 | 1408 | 30.6114  | 49.5056  |                6.35086  |    nan        |
| day_ahead_price | LightGBM                 |  18 | 1408 | 30.63    | 50.2279  |                6.29411  |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  18 | 1408 | 32.6874  | 55.8051  |                0        |      0.611664 |
| day_ahead_price | Hour-of-week climatology |  18 | 1408 | 40.8405  | 67.0462  |              -24.9426   |    nan        |
| day_ahead_price | Timestral 209M           |  19 | 1408 | 31.1432  | 53.7795  |               21.0712   |      0.750356 |
| day_ahead_price | TimesFM 3.0              |  19 | 1408 | 31.4386  | 54.7441  |               20.3224   |      0.76458  |
| day_ahead_price | Timestral 28M            |  19 | 1408 | 31.472   | 53.9762  |               20.2378   |      0.765292 |
| day_ahead_price | Chronos-2                |  19 | 1408 | 31.9473  | 55.259   |               19.0332   |      0.740398 |
| day_ahead_price | LightGBM                 |  19 | 1408 | 35.0412  | 56.8743  |               11.1922   |    nan        |
| day_ahead_price | XGBoost                  |  19 | 1408 | 35.133   | 56.2914  |               10.9594   |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  19 | 1408 | 39.4573  | 65.4736  |                0        |      0.573969 |
| day_ahead_price | Hour-of-week climatology |  19 | 1408 | 46.7492  | 74.3132  |              -18.4803   |    nan        |
| day_ahead_price | TimesFM 3.0              |  20 | 1408 | 29.5145  | 47.8654  |               20.2105   |      0.748933 |
| day_ahead_price | Timestral 28M            |  20 | 1408 | 29.7476  | 47.6018  |               19.5802   |      0.744666 |
| day_ahead_price | Timestral 209M           |  20 | 1408 | 29.8843  | 47.3162  |               19.2108   |      0.732575 |
| day_ahead_price | Chronos-2                |  20 | 1408 | 30.1608  | 47.8673  |               18.4633   |      0.706259 |
| day_ahead_price | XGBoost                  |  20 | 1408 | 33.4226  | 50.5457  |                9.64528  |    nan        |
| day_ahead_price | LightGBM                 |  20 | 1408 | 33.8871  | 51.1232  |                8.38944  |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  20 | 1408 | 36.9904  | 56.7146  |                0        |      0.562589 |
| day_ahead_price | Hour-of-week climatology |  20 | 1408 | 39.6839  | 60.9733  |               -7.28164  |    nan        |
| day_ahead_price | Timestral 28M            |  21 | 1408 | 22.1903  | 35.1299  |               15.2964   |      0.793741 |
| day_ahead_price | Timestral 209M           |  21 | 1408 | 22.3274  | 34.9296  |               14.773    |      0.766003 |
| day_ahead_price | Chronos-2                |  21 | 1408 | 22.5153  | 34.7279  |               14.0558   |      0.743954 |
| day_ahead_price | TimesFM 3.0              |  21 | 1408 | 22.5681  | 35.6988  |               13.854    |      0.79303  |
| day_ahead_price | XGBoost                  |  21 | 1408 | 25.8509  | 38.9362  |                1.32311  |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  21 | 1408 | 26.1975  | 40.3627  |                0        |      0.657183 |
| day_ahead_price | LightGBM                 |  21 | 1408 | 26.3231  | 39.6745  |               -0.479148 |    nan        |
| day_ahead_price | Hour-of-week climatology |  21 | 1408 | 37.6575  | 54.2382  |              -43.7443   |    nan        |
| day_ahead_price | Timestral 28M            |  22 | 1408 | 17.5307  | 25.9911  |               10.3027   |      0.823613 |
| day_ahead_price | Timestral 209M           |  22 | 1408 | 17.5367  | 25.9283  |               10.2722   |      0.795164 |
| day_ahead_price | Chronos-2                |  22 | 1408 | 17.8365  | 26.1566  |                8.73821  |      0.785917 |
| day_ahead_price | TimesFM 3.0              |  22 | 1408 | 17.9243  | 26.7664  |                8.28909  |      0.84495  |
| day_ahead_price | Seasonal naive (24h)     |  22 | 1408 | 19.5443  | 29.561   |                0        |      0.731863 |
| day_ahead_price | XGBoost                  |  22 | 1408 | 20.5422  | 29.006   |               -5.10596  |    nan        |
| day_ahead_price | LightGBM                 |  22 | 1408 | 20.9445  | 29.508   |               -7.1641   |    nan        |
| day_ahead_price | Hour-of-week climatology |  22 | 1408 | 42.8957  | 61.5776  |             -119.479    |    nan        |
| day_ahead_price | Timestral 28M            |  23 | 1408 | 16.1839  | 23.6889  |                9.10105  |      0.811522 |
| day_ahead_price | Timestral 209M           |  23 | 1408 | 16.2629  | 23.7406  |                8.65691  |      0.79872  |
| day_ahead_price | Chronos-2                |  23 | 1408 | 16.6192  | 24.2711  |                6.65589  |      0.800142 |
| day_ahead_price | TimesFM 3.0              |  23 | 1408 | 16.8376  | 24.7566  |                5.42925  |      0.842105 |
| day_ahead_price | Seasonal naive (24h)     |  23 | 1408 | 17.8042  | 26.5217  |                0        |      0.744666 |
| day_ahead_price | XGBoost                  |  23 | 1408 | 18.5267  | 25.9864  |               -4.05782  |    nan        |
| day_ahead_price | LightGBM                 |  23 | 1408 | 18.6295  | 25.9329  |               -4.63544  |    nan        |
| day_ahead_price | Hour-of-week climatology |  23 | 1408 | 37.3361  | 54.6024  |             -109.704    |    nan        |
| day_ahead_price | Timestral 28M            |  24 | 1408 | 18.1958  | 26.6663  |                9.11348  |      0.776671 |
| day_ahead_price | Timestral 209M           |  24 | 1408 | 18.2602  | 26.8227  |                8.79212  |      0.75889  |
| day_ahead_price | Chronos-2                |  24 | 1408 | 18.5628  | 27.3303  |                7.28046  |      0.755334 |
| day_ahead_price | TimesFM 3.0              |  24 | 1408 | 18.6314  | 27.5168  |                6.93798  |      0.805832 |
| day_ahead_price | LightGBM                 |  24 | 1408 | 19.4976  | 27.6561  |                2.61125  |    nan        |
| day_ahead_price | XGBoost                  |  24 | 1408 | 19.6562  | 28.0692  |                1.81922  |    nan        |
| day_ahead_price | Seasonal naive (24h)     |  24 | 1408 | 20.0204  | 30.0971  |                0        |      0.728307 |
| day_ahead_price | Hour-of-week climatology |  24 | 1408 | 38.7405  | 52.3593  |              -93.5051   |    nan        |