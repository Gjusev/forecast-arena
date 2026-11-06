# Event detection

| model                    | series_id                        |   h |   evt_n_events |   evt_precision |   evt_recall |      evt_f1 |
|:-------------------------|:---------------------------------|----:|---------------:|----------------:|-------------:|------------:|
| Chronos-2                | avg_delay_min/Berlin Hbf         |   1 |              2 |       0.333333  |    0.5       |   0.4       |
| Chronos-2                | avg_delay_min/Berlin Hbf         |   3 |              6 |       0.5       |    0.166667  |   0.25      |
| Chronos-2                | avg_delay_min/Berlin Hbf         |   6 |              7 |       1         |    0.142857  |   0.25      |
| Chronos-2                | avg_delay_min/Berlin Hbf         |  24 |              8 |       1         |    0.125     |   0.222222  |
| Chronos-2                | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.647059  |    0.478261  |   0.55      |
| Chronos-2                | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.642857  |    0.391304  |   0.486486  |
| Chronos-2                | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.833333  |    0.416667  |   0.555556  |
| Chronos-2                | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.545455  |    0.333333  |   0.413793  |
| Chronos-2                | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.75      |    0.545455  |   0.631579  |
| Chronos-2                | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.375     |    0.2       |   0.26087   |
| Chronos-2                | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.555556  |    0.294118  |   0.384615  |
| Chronos-2                | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0         |    0         | nan         |
| Chronos-2                | avg_delay_min/Köln Hbf           |   1 |             17 |       0.545455  |    0.352941  |   0.428571  |
| Chronos-2                | avg_delay_min/Köln Hbf           |   3 |             21 |       0.555556  |    0.238095  |   0.333333  |
| Chronos-2                | avg_delay_min/Köln Hbf           |   6 |             22 |       0.692308  |    0.409091  |   0.514286  |
| Chronos-2                | avg_delay_min/Köln Hbf           |  24 |             25 |       0.666667  |    0.08      |   0.142857  |
| Chronos-2                | avg_delay_min/München Hbf        |   1 |              5 |       0.5       |    0.4       |   0.444444  |
| Chronos-2                | avg_delay_min/München Hbf        |   3 |             15 |       0         |    0         | nan         |
| Chronos-2                | avg_delay_min/München Hbf        |   6 |              9 |       0.333333  |    0.111111  |   0.166667  |
| Chronos-2                | avg_delay_min/München Hbf        |  24 |              9 |     nan         |    0         | nan         |
| Chronos-2                | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0.714286  |    0.277778  |   0.4       |
| Chronos-2                | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0.571429  |    0.307692  |   0.4       |
| Chronos-2                | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.5       |    0.3       |   0.375     |
| Chronos-2                | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.25      |    0.0555556 |   0.0909091 |
| Chronos-2                | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.766667  |    0.638889  |   0.69697   |
| Chronos-2                | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.6       |    0.681818  |   0.638298  |
| Chronos-2                | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.789474  |    0.576923  |   0.666667  |
| Chronos-2                | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.777778  |    0.84      |   0.807692  |
| Chronos-2                | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.846154  |    0.458333  |   0.594595  |
| Chronos-2                | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.941176  |    0.592593  |   0.727273  |
| Chronos-2                | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.705882  |    0.413793  |   0.521739  |
| Chronos-2                | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.785714  |    0.458333  |   0.578947  |
| Chronos-2                | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.619048  |    0.481481  |   0.541667  |
| Chronos-2                | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.666667  |    0.857143  |   0.75      |
| Chronos-2                | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.714286  |    0.555556  |   0.625     |
| Chronos-2                | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.863636  |    0.612903  |   0.716981  |
| Chronos-2                | n_delayed_gt5/München Hbf        |   1 |              4 |       0.5       |    0.25      |   0.333333  |
| Chronos-2                | n_delayed_gt5/München Hbf        |   3 |              3 |       1         |    0.333333  |   0.5       |
| Chronos-2                | n_delayed_gt5/München Hbf        |   6 |              7 |       1         |    0.285714  |   0.444444  |
| Chronos-2                | n_delayed_gt5/München Hbf        |  24 |              9 |       1         |    0.222222  |   0.363636  |
| Hour-of-week climatology | avg_delay_min/Berlin Hbf         |   1 |              2 |       0         |    0         | nan         |
| Hour-of-week climatology | avg_delay_min/Berlin Hbf         |   3 |              6 |       0.111111  |    0.166667  |   0.133333  |
| Hour-of-week climatology | avg_delay_min/Berlin Hbf         |   6 |              7 |       0         |    0         | nan         |
| Hour-of-week climatology | avg_delay_min/Berlin Hbf         |  24 |              8 |       1         |    0.125     |   0.222222  |
| Hour-of-week climatology | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.227273  |    0.217391  |   0.222222  |
| Hour-of-week climatology | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.26087   |    0.26087   |   0.26087   |
| Hour-of-week climatology | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.2       |    0.166667  |   0.181818  |
| Hour-of-week climatology | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.2       |    0.222222  |   0.210526  |
| Hour-of-week climatology | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.1       |    0.0909091 |   0.0952381 |
| Hour-of-week climatology | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.0555556 |    0.0666667 |   0.0606061 |
| Hour-of-week climatology | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.25      |    0.235294  |   0.242424  |
| Hour-of-week climatology | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0.166667  |    0.133333  |   0.148148  |
| Hour-of-week climatology | avg_delay_min/Köln Hbf           |   1 |             17 |       0.2       |    0.117647  |   0.148148  |
| Hour-of-week climatology | avg_delay_min/Köln Hbf           |   3 |             21 |       0.111111  |    0.0952381 |   0.102564  |
| Hour-of-week climatology | avg_delay_min/Köln Hbf           |   6 |             22 |       0.166667  |    0.0909091 |   0.117647  |
| Hour-of-week climatology | avg_delay_min/Köln Hbf           |  24 |             25 |       0.333333  |    0.12      |   0.176471  |
| Hour-of-week climatology | avg_delay_min/München Hbf        |   1 |              5 |       0         |    0         | nan         |
| Hour-of-week climatology | avg_delay_min/München Hbf        |   3 |             15 |       0.133333  |    0.133333  |   0.133333  |
| Hour-of-week climatology | avg_delay_min/München Hbf        |   6 |              9 |       0.222222  |    0.222222  |   0.222222  |
| Hour-of-week climatology | avg_delay_min/München Hbf        |  24 |              9 |       0.214286  |    0.333333  |   0.26087   |
| Hour-of-week climatology | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0         |    0         | nan         |
| Hour-of-week climatology | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0         |    0         | nan         |
| Hour-of-week climatology | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.5       |    0.3       |   0.375     |
| Hour-of-week climatology | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.25      |    0.0555556 |   0.0909091 |
| Hour-of-week climatology | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.40625   |    0.361111  |   0.382353  |
| Hour-of-week climatology | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.206897  |    0.272727  |   0.235294  |
| Hour-of-week climatology | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.192308  |    0.192308  |   0.192308  |
| Hour-of-week climatology | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.222222  |    0.32      |   0.262295  |
| Hour-of-week climatology | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.266667  |    0.166667  |   0.205128  |
| Hour-of-week climatology | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.0625    |    0.037037  |   0.0465116 |
| Hour-of-week climatology | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.24      |    0.206897  |   0.222222  |
| Hour-of-week climatology | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.1875    |    0.125     |   0.15      |
| Hour-of-week climatology | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.28      |    0.259259  |   0.269231  |
| Hour-of-week climatology | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.105263  |    0.0952381 |   0.1       |
| Hour-of-week climatology | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.315789  |    0.222222  |   0.26087   |
| Hour-of-week climatology | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.4       |    0.387097  |   0.393443  |
| Hour-of-week climatology | n_delayed_gt5/München Hbf        |   1 |              4 |       0.25      |    0.25      |   0.25      |
| Hour-of-week climatology | n_delayed_gt5/München Hbf        |   3 |              3 |       0         |    0         | nan         |
| Hour-of-week climatology | n_delayed_gt5/München Hbf        |   6 |              7 |       0         |    0         | nan         |
| Hour-of-week climatology | n_delayed_gt5/München Hbf        |  24 |              9 |       0.0769231 |    0.111111  |   0.0909091 |
| LightGBM                 | avg_delay_min/Berlin Hbf         |   1 |              2 |       1         |    0.5       |   0.666667  |
| LightGBM                 | avg_delay_min/Berlin Hbf         |   3 |              6 |       0.5       |    0.166667  |   0.25      |
| LightGBM                 | avg_delay_min/Berlin Hbf         |   6 |              7 |       0         |    0         | nan         |
| LightGBM                 | avg_delay_min/Berlin Hbf         |  24 |              8 |     nan         |    0         | nan         |
| LightGBM                 | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.55      |    0.478261  |   0.511628  |
| LightGBM                 | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.454545  |    0.434783  |   0.444444  |
| LightGBM                 | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.631579  |    0.5       |   0.55814   |
| LightGBM                 | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.6       |    0.333333  |   0.428571  |
| LightGBM                 | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.642857  |    0.818182  |   0.72      |
| LightGBM                 | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.384615  |    0.333333  |   0.357143  |
| LightGBM                 | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.4375    |    0.411765  |   0.424242  |
| LightGBM                 | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0.5       |    0.266667  |   0.347826  |
| LightGBM                 | avg_delay_min/Köln Hbf           |   1 |             17 |       0.4       |    0.352941  |   0.375     |
| LightGBM                 | avg_delay_min/Köln Hbf           |   3 |             21 |       0.5       |    0.238095  |   0.322581  |
| LightGBM                 | avg_delay_min/Köln Hbf           |   6 |             22 |       0.470588  |    0.363636  |   0.410256  |
| LightGBM                 | avg_delay_min/Köln Hbf           |  24 |             25 |       0.642857  |    0.36      |   0.461538  |
| LightGBM                 | avg_delay_min/München Hbf        |   1 |              5 |       0.5       |    0.4       |   0.444444  |
| LightGBM                 | avg_delay_min/München Hbf        |   3 |             15 |       0         |    0         | nan         |
| LightGBM                 | avg_delay_min/München Hbf        |   6 |              9 |       0.333333  |    0.222222  |   0.266667  |
| LightGBM                 | avg_delay_min/München Hbf        |  24 |              9 |       0         |    0         | nan         |
| LightGBM                 | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0.777778  |    0.388889  |   0.518519  |
| LightGBM                 | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0.75      |    0.461538  |   0.571429  |
| LightGBM                 | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.428571  |    0.3       |   0.352941  |
| LightGBM                 | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.4       |    0.111111  |   0.173913  |
| LightGBM                 | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.741935  |    0.638889  |   0.686567  |
| LightGBM                 | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.583333  |    0.636364  |   0.608696  |
| LightGBM                 | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.772727  |    0.653846  |   0.708333  |
| LightGBM                 | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.714286  |    0.8       |   0.754717  |
| LightGBM                 | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.882353  |    0.625     |   0.731707  |
| LightGBM                 | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.888889  |    0.592593  |   0.711111  |
| LightGBM                 | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.6       |    0.413793  |   0.489796  |
| LightGBM                 | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.647059  |    0.458333  |   0.536585  |
| LightGBM                 | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.714286  |    0.555556  |   0.625     |
| LightGBM                 | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.818182  |    0.857143  |   0.837209  |
| LightGBM                 | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.666667  |    0.518519  |   0.583333  |
| LightGBM                 | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.869565  |    0.645161  |   0.740741  |
| LightGBM                 | n_delayed_gt5/München Hbf        |   1 |              4 |       0.666667  |    0.5       |   0.571429  |
| LightGBM                 | n_delayed_gt5/München Hbf        |   3 |              3 |       0         |    0         | nan         |
| LightGBM                 | n_delayed_gt5/München Hbf        |   6 |              7 |       0.5       |    0.142857  |   0.222222  |
| LightGBM                 | n_delayed_gt5/München Hbf        |  24 |              9 |       0.666667  |    0.222222  |   0.333333  |
| Seasonal naive (24h)     | avg_delay_min/Berlin Hbf         |   1 |              2 |       0         |    0         | nan         |
| Seasonal naive (24h)     | avg_delay_min/Berlin Hbf         |   3 |              6 |       0         |    0         | nan         |
| Seasonal naive (24h)     | avg_delay_min/Berlin Hbf         |   6 |              7 |       0         |    0         | nan         |
| Seasonal naive (24h)     | avg_delay_min/Berlin Hbf         |  24 |              8 |       0.2       |    0.125     |   0.153846  |
| Seasonal naive (24h)     | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.407407  |    0.478261  |   0.44      |
| Seasonal naive (24h)     | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.272727  |    0.26087   |   0.266667  |
| Seasonal naive (24h)     | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.4       |    0.333333  |   0.363636  |
| Seasonal naive (24h)     | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.416667  |    0.555556  |   0.47619   |
| Seasonal naive (24h)     | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.266667  |    0.363636  |   0.307692  |
| Seasonal naive (24h)     | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.0588235 |    0.0666667 |   0.0625    |
| Seasonal naive (24h)     | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.333333  |    0.352941  |   0.342857  |
| Seasonal naive (24h)     | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0.352941  |    0.4       |   0.375     |
| Seasonal naive (24h)     | avg_delay_min/Köln Hbf           |   1 |             17 |       0.285714  |    0.235294  |   0.258065  |
| Seasonal naive (24h)     | avg_delay_min/Köln Hbf           |   3 |             21 |       0.157895  |    0.142857  |   0.15      |
| Seasonal naive (24h)     | avg_delay_min/Köln Hbf           |   6 |             22 |       0.3125    |    0.227273  |   0.263158  |
| Seasonal naive (24h)     | avg_delay_min/Köln Hbf           |  24 |             25 |       0.363636  |    0.32      |   0.340426  |
| Seasonal naive (24h)     | avg_delay_min/München Hbf        |   1 |              5 |       0         |    0         | nan         |
| Seasonal naive (24h)     | avg_delay_min/München Hbf        |   3 |             15 |       0.263158  |    0.333333  |   0.294118  |
| Seasonal naive (24h)     | avg_delay_min/München Hbf        |   6 |              9 |       0.111111  |    0.222222  |   0.148148  |
| Seasonal naive (24h)     | avg_delay_min/München Hbf        |  24 |              9 |       0.166667  |    0.111111  |   0.133333  |
| Seasonal naive (24h)     | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0.363636  |    0.222222  |   0.275862  |
| Seasonal naive (24h)     | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0.294118  |    0.384615  |   0.333333  |
| Seasonal naive (24h)     | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.4       |    0.4       |   0.4       |
| Seasonal naive (24h)     | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.214286  |    0.166667  |   0.1875    |
| Seasonal naive (24h)     | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.588235  |    0.555556  |   0.571429  |
| Seasonal naive (24h)     | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.37931   |    0.5       |   0.431373  |
| Seasonal naive (24h)     | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.65      |    0.5       |   0.565217  |
| Seasonal naive (24h)     | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.655172  |    0.76      |   0.703704  |
| Seasonal naive (24h)     | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.608696  |    0.583333  |   0.595745  |
| Seasonal naive (24h)     | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.625     |    0.555556  |   0.588235  |
| Seasonal naive (24h)     | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.6       |    0.517241  |   0.555556  |
| Seasonal naive (24h)     | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.478261  |    0.458333  |   0.468085  |
| Seasonal naive (24h)     | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.5       |    0.592593  |   0.542373  |
| Seasonal naive (24h)     | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.5       |    0.761905  |   0.603774  |
| Seasonal naive (24h)     | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.608696  |    0.518519  |   0.56      |
| Seasonal naive (24h)     | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.576923  |    0.483871  |   0.526316  |
| Seasonal naive (24h)     | n_delayed_gt5/München Hbf        |   1 |              4 |       0.166667  |    0.5       |   0.25      |
| Seasonal naive (24h)     | n_delayed_gt5/München Hbf        |   3 |              3 |       0.0909091 |    0.333333  |   0.142857  |
| Seasonal naive (24h)     | n_delayed_gt5/München Hbf        |   6 |              7 |       0.1       |    0.142857  |   0.117647  |
| Seasonal naive (24h)     | n_delayed_gt5/München Hbf        |  24 |              9 |       0.714286  |    0.555556  |   0.625     |
| TimesFM 3.0              | avg_delay_min/Berlin Hbf         |   1 |              2 |       0.5       |    0.5       |   0.5       |
| TimesFM 3.0              | avg_delay_min/Berlin Hbf         |   3 |              6 |       1         |    0.166667  |   0.285714  |
| TimesFM 3.0              | avg_delay_min/Berlin Hbf         |   6 |              7 |       0.666667  |    0.285714  |   0.4       |
| TimesFM 3.0              | avg_delay_min/Berlin Hbf         |  24 |              8 |     nan         |    0         | nan         |
| TimesFM 3.0              | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.642857  |    0.391304  |   0.486486  |
| TimesFM 3.0              | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.555556  |    0.434783  |   0.487805  |
| TimesFM 3.0              | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.857143  |    0.5       |   0.631579  |
| TimesFM 3.0              | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.583333  |    0.388889  |   0.466667  |
| TimesFM 3.0              | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.727273  |    0.727273  |   0.727273  |
| TimesFM 3.0              | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.444444  |    0.266667  |   0.333333  |
| TimesFM 3.0              | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.555556  |    0.294118  |   0.384615  |
| TimesFM 3.0              | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0.5       |    0.133333  |   0.210526  |
| TimesFM 3.0              | avg_delay_min/Köln Hbf           |   1 |             17 |       0.416667  |    0.294118  |   0.344828  |
| TimesFM 3.0              | avg_delay_min/Köln Hbf           |   3 |             21 |       0.5       |    0.190476  |   0.275862  |
| TimesFM 3.0              | avg_delay_min/Köln Hbf           |   6 |             22 |       0.666667  |    0.363636  |   0.470588  |
| TimesFM 3.0              | avg_delay_min/Köln Hbf           |  24 |             25 |       0.5       |    0.04      |   0.0740741 |
| TimesFM 3.0              | avg_delay_min/München Hbf        |   1 |              5 |       0.4       |    0.4       |   0.4       |
| TimesFM 3.0              | avg_delay_min/München Hbf        |   3 |             15 |       0         |    0         | nan         |
| TimesFM 3.0              | avg_delay_min/München Hbf        |   6 |              9 |       0.666667  |    0.222222  |   0.333333  |
| TimesFM 3.0              | avg_delay_min/München Hbf        |  24 |              9 |     nan         |    0         | nan         |
| TimesFM 3.0              | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0.833333  |    0.277778  |   0.416667  |
| TimesFM 3.0              | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0.5       |    0.230769  |   0.315789  |
| TimesFM 3.0              | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.4       |    0.2       |   0.266667  |
| TimesFM 3.0              | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.25      |    0.0555556 |   0.0909091 |
| TimesFM 3.0              | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.793103  |    0.638889  |   0.707692  |
| TimesFM 3.0              | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.6       |    0.681818  |   0.638298  |
| TimesFM 3.0              | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.75      |    0.576923  |   0.652174  |
| TimesFM 3.0              | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.826087  |    0.76      |   0.791667  |
| TimesFM 3.0              | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.8125    |    0.541667  |   0.65      |
| TimesFM 3.0              | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.823529  |    0.518519  |   0.636364  |
| TimesFM 3.0              | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.666667  |    0.413793  |   0.510638  |
| TimesFM 3.0              | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.733333  |    0.458333  |   0.564103  |
| TimesFM 3.0              | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.714286  |    0.555556  |   0.625     |
| TimesFM 3.0              | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.73913   |    0.809524  |   0.772727  |
| TimesFM 3.0              | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.681818  |    0.555556  |   0.612245  |
| TimesFM 3.0              | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.842105  |    0.516129  |   0.64      |
| TimesFM 3.0              | n_delayed_gt5/München Hbf        |   1 |              4 |       0.5       |    0.25      |   0.333333  |
| TimesFM 3.0              | n_delayed_gt5/München Hbf        |   3 |              3 |       1         |    0.333333  |   0.5       |
| TimesFM 3.0              | n_delayed_gt5/München Hbf        |   6 |              7 |       1         |    0.285714  |   0.444444  |
| TimesFM 3.0              | n_delayed_gt5/München Hbf        |  24 |              9 |       1         |    0.111111  |   0.2       |
| Timestral 209M           | avg_delay_min/Berlin Hbf         |   1 |              2 |       0.5       |    0.5       |   0.5       |
| Timestral 209M           | avg_delay_min/Berlin Hbf         |   3 |              6 |       1         |    0.166667  |   0.285714  |
| Timestral 209M           | avg_delay_min/Berlin Hbf         |   6 |              7 |       0.5       |    0.142857  |   0.222222  |
| Timestral 209M           | avg_delay_min/Berlin Hbf         |  24 |              8 |     nan         |    0         | nan         |
| Timestral 209M           | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.75      |    0.521739  |   0.615385  |
| Timestral 209M           | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.615385  |    0.347826  |   0.444444  |
| Timestral 209M           | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.857143  |    0.5       |   0.631579  |
| Timestral 209M           | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.7       |    0.388889  |   0.5       |
| Timestral 209M           | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.727273  |    0.727273  |   0.727273  |
| Timestral 209M           | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.5       |    0.333333  |   0.4       |
| Timestral 209M           | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.4       |    0.235294  |   0.296296  |
| Timestral 209M           | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0         |    0         | nan         |
| Timestral 209M           | avg_delay_min/Köln Hbf           |   1 |             17 |       0.4375    |    0.411765  |   0.424242  |
| Timestral 209M           | avg_delay_min/Köln Hbf           |   3 |             21 |       0.571429  |    0.190476  |   0.285714  |
| Timestral 209M           | avg_delay_min/Köln Hbf           |   6 |             22 |       0.545455  |    0.272727  |   0.363636  |
| Timestral 209M           | avg_delay_min/Köln Hbf           |  24 |             25 |       0.666667  |    0.08      |   0.142857  |
| Timestral 209M           | avg_delay_min/München Hbf        |   1 |              5 |       0.666667  |    0.4       |   0.5       |
| Timestral 209M           | avg_delay_min/München Hbf        |   3 |             15 |       0         |    0         | nan         |
| Timestral 209M           | avg_delay_min/München Hbf        |   6 |              9 |       0.333333  |    0.111111  |   0.166667  |
| Timestral 209M           | avg_delay_min/München Hbf        |  24 |              9 |     nan         |    0         | nan         |
| Timestral 209M           | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0.777778  |    0.388889  |   0.518519  |
| Timestral 209M           | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0.625     |    0.384615  |   0.47619   |
| Timestral 209M           | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.333333  |    0.2       |   0.25      |
| Timestral 209M           | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.25      |    0.0555556 |   0.0909091 |
| Timestral 209M           | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.758621  |    0.611111  |   0.676923  |
| Timestral 209M           | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.56      |    0.636364  |   0.595745  |
| Timestral 209M           | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.8       |    0.615385  |   0.695652  |
| Timestral 209M           | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.857143  |    0.72      |   0.782609  |
| Timestral 209M           | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.882353  |    0.625     |   0.731707  |
| Timestral 209M           | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.875     |    0.518519  |   0.651163  |
| Timestral 209M           | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.647059  |    0.37931   |   0.478261  |
| Timestral 209M           | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.636364  |    0.291667  |   0.4       |
| Timestral 209M           | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.681818  |    0.555556  |   0.612245  |
| Timestral 209M           | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.73913   |    0.809524  |   0.772727  |
| Timestral 209M           | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.7       |    0.518519  |   0.595745  |
| Timestral 209M           | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.85      |    0.548387  |   0.666667  |
| Timestral 209M           | n_delayed_gt5/München Hbf        |   1 |              4 |       0.5       |    0.25      |   0.333333  |
| Timestral 209M           | n_delayed_gt5/München Hbf        |   3 |              3 |       1         |    0.333333  |   0.5       |
| Timestral 209M           | n_delayed_gt5/München Hbf        |   6 |              7 |       1         |    0.285714  |   0.444444  |
| Timestral 209M           | n_delayed_gt5/München Hbf        |  24 |              9 |       1         |    0.222222  |   0.363636  |
| Timestral 28M            | avg_delay_min/Berlin Hbf         |   1 |              2 |       0.5       |    0.5       |   0.5       |
| Timestral 28M            | avg_delay_min/Berlin Hbf         |   3 |              6 |       1         |    0.166667  |   0.285714  |
| Timestral 28M            | avg_delay_min/Berlin Hbf         |   6 |              7 |       0.5       |    0.142857  |   0.222222  |
| Timestral 28M            | avg_delay_min/Berlin Hbf         |  24 |              8 |     nan         |    0         | nan         |
| Timestral 28M            | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.714286  |    0.434783  |   0.540541  |
| Timestral 28M            | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.692308  |    0.391304  |   0.5       |
| Timestral 28M            | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.9       |    0.375     |   0.529412  |
| Timestral 28M            | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.666667  |    0.333333  |   0.444444  |
| Timestral 28M            | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.666667  |    0.727273  |   0.695652  |
| Timestral 28M            | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.3       |    0.2       |   0.24      |
| Timestral 28M            | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.454545  |    0.294118  |   0.357143  |
| Timestral 28M            | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0         |    0         | nan         |
| Timestral 28M            | avg_delay_min/Köln Hbf           |   1 |             17 |       0.583333  |    0.411765  |   0.482759  |
| Timestral 28M            | avg_delay_min/Köln Hbf           |   3 |             21 |       0.428571  |    0.142857  |   0.214286  |
| Timestral 28M            | avg_delay_min/Köln Hbf           |   6 |             22 |       0.615385  |    0.363636  |   0.457143  |
| Timestral 28M            | avg_delay_min/Köln Hbf           |  24 |             25 |       0         |    0         | nan         |
| Timestral 28M            | avg_delay_min/München Hbf        |   1 |              5 |       0.5       |    0.4       |   0.444444  |
| Timestral 28M            | avg_delay_min/München Hbf        |   3 |             15 |       0         |    0         | nan         |
| Timestral 28M            | avg_delay_min/München Hbf        |   6 |              9 |       0.333333  |    0.111111  |   0.166667  |
| Timestral 28M            | avg_delay_min/München Hbf        |  24 |              9 |     nan         |    0         | nan         |
| Timestral 28M            | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0.75      |    0.333333  |   0.461538  |
| Timestral 28M            | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0.666667  |    0.461538  |   0.545455  |
| Timestral 28M            | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.2       |    0.1       |   0.133333  |
| Timestral 28M            | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.25      |    0.0555556 |   0.0909091 |
| Timestral 28M            | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.75      |    0.583333  |   0.65625   |
| Timestral 28M            | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.541667  |    0.590909  |   0.565217  |
| Timestral 28M            | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.8       |    0.615385  |   0.695652  |
| Timestral 28M            | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.863636  |    0.76      |   0.808511  |
| Timestral 28M            | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.866667  |    0.541667  |   0.666667  |
| Timestral 28M            | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.833333  |    0.555556  |   0.666667  |
| Timestral 28M            | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.590909  |    0.448276  |   0.509804  |
| Timestral 28M            | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.642857  |    0.375     |   0.473684  |
| Timestral 28M            | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.681818  |    0.555556  |   0.612245  |
| Timestral 28M            | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.826087  |    0.904762  |   0.863636  |
| Timestral 28M            | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.652174  |    0.555556  |   0.6       |
| Timestral 28M            | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.857143  |    0.580645  |   0.692308  |
| Timestral 28M            | n_delayed_gt5/München Hbf        |   1 |              4 |       1         |    0.25      |   0.4       |
| Timestral 28M            | n_delayed_gt5/München Hbf        |   3 |              3 |     nan         |    0         | nan         |
| Timestral 28M            | n_delayed_gt5/München Hbf        |   6 |              7 |       1         |    0.285714  |   0.444444  |
| Timestral 28M            | n_delayed_gt5/München Hbf        |  24 |              9 |       1         |    0.111111  |   0.2       |
| XGBoost                  | avg_delay_min/Berlin Hbf         |   1 |              2 |       0.5       |    0.5       |   0.5       |
| XGBoost                  | avg_delay_min/Berlin Hbf         |   3 |              6 |       0.5       |    0.166667  |   0.25      |
| XGBoost                  | avg_delay_min/Berlin Hbf         |   6 |              7 |       0.333333  |    0.142857  |   0.2       |
| XGBoost                  | avg_delay_min/Berlin Hbf         |  24 |              8 |     nan         |    0         | nan         |
| XGBoost                  | avg_delay_min/Frankfurt(Main)Hbf |   1 |             23 |       0.65      |    0.565217  |   0.604651  |
| XGBoost                  | avg_delay_min/Frankfurt(Main)Hbf |   3 |             23 |       0.55      |    0.478261  |   0.511628  |
| XGBoost                  | avg_delay_min/Frankfurt(Main)Hbf |   6 |             24 |       0.611111  |    0.458333  |   0.52381   |
| XGBoost                  | avg_delay_min/Frankfurt(Main)Hbf |  24 |             18 |       0.636364  |    0.388889  |   0.482759  |
| XGBoost                  | avg_delay_min/Hamburg Hbf        |   1 |             11 |       0.529412  |    0.818182  |   0.642857  |
| XGBoost                  | avg_delay_min/Hamburg Hbf        |   3 |             15 |       0.363636  |    0.266667  |   0.307692  |
| XGBoost                  | avg_delay_min/Hamburg Hbf        |   6 |             17 |       0.375     |    0.352941  |   0.363636  |
| XGBoost                  | avg_delay_min/Hamburg Hbf        |  24 |             15 |       0.555556  |    0.333333  |   0.416667  |
| XGBoost                  | avg_delay_min/Köln Hbf           |   1 |             17 |       0.4       |    0.352941  |   0.375     |
| XGBoost                  | avg_delay_min/Köln Hbf           |   3 |             21 |       0.461538  |    0.285714  |   0.352941  |
| XGBoost                  | avg_delay_min/Köln Hbf           |   6 |             22 |       0.526316  |    0.454545  |   0.487805  |
| XGBoost                  | avg_delay_min/Köln Hbf           |  24 |             25 |       0.7       |    0.28      |   0.4       |
| XGBoost                  | avg_delay_min/München Hbf        |   1 |              5 |       0.5       |    0.4       |   0.444444  |
| XGBoost                  | avg_delay_min/München Hbf        |   3 |             15 |       0         |    0         | nan         |
| XGBoost                  | avg_delay_min/München Hbf        |   6 |              9 |       0.285714  |    0.222222  |   0.25      |
| XGBoost                  | avg_delay_min/München Hbf        |  24 |              9 |       0.5       |    0.111111  |   0.181818  |
| XGBoost                  | n_delayed_gt5/Berlin Hbf         |   1 |             18 |       0.8       |    0.444444  |   0.571429  |
| XGBoost                  | n_delayed_gt5/Berlin Hbf         |   3 |             13 |       0.857143  |    0.461538  |   0.6       |
| XGBoost                  | n_delayed_gt5/Berlin Hbf         |   6 |             10 |       0.666667  |    0.2       |   0.307692  |
| XGBoost                  | n_delayed_gt5/Berlin Hbf         |  24 |             18 |       0.4       |    0.111111  |   0.173913  |
| XGBoost                  | n_delayed_gt5/Frankfurt(Main)Hbf |   1 |             36 |       0.766667  |    0.638889  |   0.69697   |
| XGBoost                  | n_delayed_gt5/Frankfurt(Main)Hbf |   3 |             22 |       0.565217  |    0.590909  |   0.577778  |
| XGBoost                  | n_delayed_gt5/Frankfurt(Main)Hbf |   6 |             26 |       0.8       |    0.615385  |   0.695652  |
| XGBoost                  | n_delayed_gt5/Frankfurt(Main)Hbf |  24 |             25 |       0.730769  |    0.76      |   0.745098  |
| XGBoost                  | n_delayed_gt5/Hamburg Hbf        |   1 |             24 |       0.882353  |    0.625     |   0.731707  |
| XGBoost                  | n_delayed_gt5/Hamburg Hbf        |   3 |             27 |       0.866667  |    0.481481  |   0.619048  |
| XGBoost                  | n_delayed_gt5/Hamburg Hbf        |   6 |             29 |       0.647059  |    0.37931   |   0.478261  |
| XGBoost                  | n_delayed_gt5/Hamburg Hbf        |  24 |             24 |       0.666667  |    0.416667  |   0.512821  |
| XGBoost                  | n_delayed_gt5/Köln Hbf           |   1 |             27 |       0.666667  |    0.518519  |   0.583333  |
| XGBoost                  | n_delayed_gt5/Köln Hbf           |   3 |             21 |       0.772727  |    0.809524  |   0.790698  |
| XGBoost                  | n_delayed_gt5/Köln Hbf           |   6 |             27 |       0.705882  |    0.444444  |   0.545455  |
| XGBoost                  | n_delayed_gt5/Köln Hbf           |  24 |             31 |       0.826087  |    0.612903  |   0.703704  |
| XGBoost                  | n_delayed_gt5/München Hbf        |   1 |              4 |       0.666667  |    0.5       |   0.571429  |
| XGBoost                  | n_delayed_gt5/München Hbf        |   3 |              3 |       0         |    0         | nan         |
| XGBoost                  | n_delayed_gt5/München Hbf        |   6 |              7 |       1         |    0.142857  |   0.25      |
| XGBoost                  | n_delayed_gt5/München Hbf        |  24 |              9 |       0.5       |    0.111111  |   0.181818  |