# Diebold-Mariano vs seasonal naive (|error| loss)

Negative statistic = fewer losses than the baseline. p-value from a HAC normal approximation; treat families of tests with a multiple-testing caveat (28 model-horizon tests here).

| model                    |   h |    dm_stat |      p_value | better_than_baseline   |
|:-------------------------|----:|-----------:|-------------:|:-----------------------|
| Timestral 209M           |   1 | -23.5476   | 1.32714e-122 | True                   |
| Timestral 28M            |   1 | -23.4402   | 1.66405e-121 | True                   |
| TimesFM 3.0              |   1 | -23.3566   | 1.18081e-120 | True                   |
| Chronos-2                |   1 | -23.3065   | 3.80944e-120 | True                   |
| LightGBM                 |   1 | -23.1377   | 1.93245e-118 | True                   |
| XGBoost                  |   1 | -22.9104   | 3.65773e-116 | True                   |
| Hour-of-week climatology |   1 |  16.4154   | 1.48484e-60  | False                  |
| Timestral 28M            |   2 | -20.5407   | 9.32498e-94  | True                   |
| Timestral 209M           |   2 | -20.4761   | 3.51381e-93  | True                   |
| Chronos-2                |   2 | -20.3254   | 7.66864e-92  | True                   |
| TimesFM 3.0              |   2 | -19.897    | 4.31672e-88  | True                   |
| LightGBM                 |   2 | -19.0357   | 8.63934e-81  | True                   |
| XGBoost                  |   2 | -18.8225   | 4.94089e-79  | True                   |
| Hour-of-week climatology |   2 |  16.5667   | 1.21345e-61  | False                  |
| Timestral 28M            |   3 | -18.5956   | 3.4895e-77   | True                   |
| Timestral 209M           |   3 | -18.5549   | 7.44238e-77  | True                   |
| Chronos-2                |   3 | -18.3838   | 1.77163e-75  | True                   |
| TimesFM 3.0              |   3 | -17.9475   | 5.02245e-72  | True                   |
| LightGBM                 |   3 | -16.4946   | 4.0106e-61   | True                   |
| XGBoost                  |   3 | -16.1052   | 2.34428e-58  | True                   |
| Hour-of-week climatology |   3 |  15.6938   | 1.66636e-55  | False                  |
| Timestral 209M           |   4 | -16.8814   | 6.16573e-64  | True                   |
| Timestral 28M            |   4 | -16.8756   | 6.8023e-64   | True                   |
| Chronos-2                |   4 | -16.6553   | 2.76846e-62  | True                   |
| TimesFM 3.0              |   4 | -16.3599   | 3.6955e-60   | True                   |
| Hour-of-week climatology |   4 |  14.6765   | 9.11741e-49  | False                  |
| LightGBM                 |   4 | -14.4143   | 4.20628e-47  | True                   |
| XGBoost                  |   4 | -13.8177   | 1.994e-43    | True                   |
| Timestral 209M           |   5 | -15.3172   | 5.86811e-53  | True                   |
| Timestral 28M            |   5 | -15.191    | 4.05663e-52  | True                   |
| Chronos-2                |   5 | -15.1811   | 4.72008e-52  | True                   |
| TimesFM 3.0              |   5 | -14.9037   | 3.11672e-50  | True                   |
| Hour-of-week climatology |   5 |  14.3482   | 1.0937e-46   | False                  |
| LightGBM                 |   5 | -13.0156   | 9.97689e-39  | True                   |
| XGBoost                  |   5 | -11.5743   | 5.56354e-31  | True                   |
| Chronos-2                |   6 | -17.0659   | 2.66348e-65  | True                   |
| TimesFM 3.0              |   6 | -16.6965   | 1.3888e-62   | True                   |
| Timestral 209M           |   6 | -16.3081   | 8.64277e-60  | True                   |
| Timestral 28M            |   6 | -15.716    | 1.17572e-55  | True                   |
| Hour-of-week climatology |   6 |  14.4126   | 4.31224e-47  | False                  |
| LightGBM                 |   6 | -14.3778   | 7.13351e-47  | True                   |
| XGBoost                  |   6 | -13.0868   | 3.9162e-39   | True                   |
| Chronos-2                |   7 | -19.0494   | 6.64542e-81  | True                   |
| TimesFM 3.0              |   7 | -18.632    | 1.76763e-77  | True                   |
| Timestral 209M           |   7 | -17.1048   | 1.36716e-65  | True                   |
| Timestral 28M            |   7 | -16.1644   | 8.9932e-59   | True                   |
| XGBoost                  |   7 | -14.8024   | 1.41311e-49  | True                   |
| LightGBM                 |   7 | -14.0594   | 6.75024e-45  | True                   |
| Hour-of-week climatology |   7 |  11.9285   | 8.40386e-33  | False                  |
| Chronos-2                |   8 | -21.0684   | 1.54976e-98  | True                   |
| TimesFM 3.0              |   8 | -20.159    | 2.24344e-90  | True                   |
| Timestral 209M           |   8 | -18.5278   | 1.23313e-76  | True                   |
| Timestral 28M            |   8 | -17.3297   | 2.80719e-67  | True                   |
| XGBoost                  |   8 | -14.8782   | 4.5674e-50   | True                   |
| LightGBM                 |   8 | -13.1962   | 9.22449e-40  | True                   |
| Hour-of-week climatology |   8 |   4.13251  | 3.58829e-05  | False                  |
| Chronos-2                |   9 | -20.861    | 1.21115e-96  | True                   |
| TimesFM 3.0              |   9 | -18.9409   | 5.24765e-80  | True                   |
| Timestral 209M           |   9 | -18.0576   | 6.87545e-73  | True                   |
| Timestral 28M            |   9 | -16.9194   | 3.23784e-64  | True                   |
| XGBoost                  |   9 | -11.0474   | 2.2574e-28   | True                   |
| LightGBM                 |   9 |  -9.53057  | 1.56422e-21  | True                   |
| Hour-of-week climatology |   9 |   4.76339  | 1.90367e-06  | False                  |
| Chronos-2                |  10 | -17.6571   | 8.97916e-70  | True                   |
| Timestral 209M           |  10 | -16.2446   | 2.43958e-59  | True                   |
| Timestral 28M            |  10 | -14.9999   | 7.35737e-51  | True                   |
| TimesFM 3.0              |  10 | -14.9772   | 1.03415e-50  | True                   |
| Hour-of-week climatology |  10 |  10.9371   | 7.66355e-28  | False                  |
| XGBoost                  |  10 |  -4.03909  | 5.366e-05    | True                   |
| LightGBM                 |  10 |  -2.71595  | 0.00660865   | True                   |
| Chronos-2                |  11 | -13.998    | 1.60286e-44  | True                   |
| Timestral 209M           |  11 | -13.0682   | 5.00253e-39  | True                   |
| Timestral 28M            |  11 | -12.2713   | 1.29141e-34  | True                   |
| TimesFM 3.0              |  11 | -12.0889   | 1.20853e-33  | True                   |
| Hour-of-week climatology |  11 |  10.2926   | 7.60649e-25  | False                  |
| LightGBM                 |  11 |   1.47197  | 0.141029     | False                  |
| XGBoost                  |  11 |  -0.124707 | 0.900755     | True                   |
| Chronos-2                |  12 | -12.7558   | 2.89529e-37  | True                   |
| Timestral 209M           |  12 | -12.1384   | 6.61124e-34  | True                   |
| Timestral 28M            |  12 | -11.6834   | 1.54883e-31  | True                   |
| TimesFM 3.0              |  12 | -10.7605   | 5.29074e-27  | True                   |
| Hour-of-week climatology |  12 |   9.02625  | 1.77649e-19  | False                  |
| LightGBM                 |  12 |   3.10206  | 0.00192177   | False                  |
| XGBoost                  |  12 |   1.45357  | 0.146065     | False                  |
| Chronos-2                |  13 | -11.3196   | 1.04963e-29  | True                   |
| Timestral 209M           |  13 | -11.2974   | 1.35138e-29  | True                   |
| Timestral 28M            |  13 | -10.5624   | 4.44939e-26  | True                   |
| TimesFM 3.0              |  13 |  -9.47357  | 2.70451e-21  | True                   |
| Hour-of-week climatology |  13 |   8.66607  | 4.47302e-18  | False                  |
| LightGBM                 |  13 |   2.85323  | 0.00432774   | False                  |
| XGBoost                  |  13 |   0.925735 | 0.354584     | False                  |
| Timestral 209M           |  14 | -10.1401   | 3.66845e-24  | True                   |
| Chronos-2                |  14 |  -9.94823  | 2.56706e-23  | True                   |
| Timestral 28M            |  14 |  -9.71818  | 2.52247e-22  | True                   |
| TimesFM 3.0              |  14 |  -8.54873  | 1.24447e-17  | True                   |
| Hour-of-week climatology |  14 |   8.28619  | 1.16936e-16  | False                  |
| LightGBM                 |  14 |   2.35572  | 0.0184867    | False                  |
| XGBoost                  |  14 |   0.398578 | 0.690204     | False                  |
| Chronos-2                |  15 | -10.648    | 1.78179e-26  | True                   |
| Timestral 209M           |  15 | -10.347    | 4.31879e-25  | True                   |
| Timestral 28M            |  15 |  -9.76069  | 1.6602e-22   | True                   |
| TimesFM 3.0              |  15 |  -8.69165  | 3.57212e-18  | True                   |
| Hour-of-week climatology |  15 |   7.99826  | 1.26185e-15  | False                  |
| LightGBM                 |  15 |   2.75153  | 0.00593182   | False                  |
| XGBoost                  |  15 |   0.999312 | 0.317643     | False                  |
| Chronos-2                |  16 | -11.5108   | 1.16406e-30  | True                   |
| Timestral 209M           |  16 | -11.3049   | 1.24054e-29  | True                   |
| Timestral 28M            |  16 | -10.3144   | 6.06459e-25  | True                   |
| TimesFM 3.0              |  16 |  -9.33408  | 1.01872e-20  | True                   |
| Hour-of-week climatology |  16 |   8.07491  | 6.75256e-16  | False                  |
| LightGBM                 |  16 |   1.64977  | 0.0989892    | False                  |
| XGBoost                  |  16 |   0.494394 | 0.621028     | False                  |
| Timestral 209M           |  17 | -11.0638   | 1.87954e-28  | True                   |
| Timestral 28M            |  17 | -10.8449   | 2.10871e-27  | True                   |
| Chronos-2                |  17 | -10.7175   | 8.42453e-27  | True                   |
| TimesFM 3.0              |  17 |  -9.99941  | 1.53308e-23  | True                   |
| Hour-of-week climatology |  17 |   6.99435  | 2.66496e-12  | False                  |
| XGBoost                  |  17 |  -1.21708  | 0.223576     | True                   |
| LightGBM                 |  17 |  -0.436081 | 0.662778     | True                   |
| Chronos-2                |  18 |  -9.69068  | 3.30328e-22  | True                   |
| Timestral 209M           |  18 |  -9.15309  | 5.53269e-20  | True                   |
| TimesFM 3.0              |  18 |  -8.96855  | 3.00456e-19  | True                   |
| Timestral 28M            |  18 |  -8.86408  | 7.71375e-19  | True                   |
| Hour-of-week climatology |  18 |   5.60591  | 2.07162e-08  | False                  |
| XGBoost                  |  18 |  -2.22023  | 0.0264033    | True                   |
| LightGBM                 |  18 |  -2.11552  | 0.0343857    | True                   |
| Chronos-2                |  19 |  -9.43074  | 4.07187e-21  | True                   |
| Timestral 28M            |  19 |  -9.06267  | 1.27294e-19  | True                   |
| Timestral 209M           |  19 |  -8.82249  | 1.11947e-18  | True                   |
| TimesFM 3.0              |  19 |  -8.18182  | 2.79594e-16  | True                   |
| Hour-of-week climatology |  19 |   5.21046  | 1.88373e-07  | False                  |
| LightGBM                 |  19 |  -4.22815  | 2.35625e-05  | True                   |
| XGBoost                  |  19 |  -3.93438  | 8.34119e-05  | True                   |
| Timestral 28M            |  20 |  -9.85501  | 6.52079e-23  | True                   |
| Timestral 209M           |  20 |  -9.70167  | 2.96605e-22  | True                   |
| TimesFM 3.0              |  20 |  -9.21327  | 3.16338e-20  | True                   |
| Chronos-2                |  20 |  -9.02589  | 1.78235e-19  | True                   |
| XGBoost                  |  20 |  -3.5114   | 0.000445746  | True                   |
| LightGBM                 |  20 |  -3.08468  | 0.00203769   | True                   |
| Hour-of-week climatology |  20 |   2.26515  | 0.0235036    | False                  |
| Hour-of-week climatology |  21 |   8.49447  | 1.98837e-17  | False                  |
| Timestral 28M            |  21 |  -7.3286   | 2.32577e-13  | True                   |
| Timestral 209M           |  21 |  -7.24885  | 4.20336e-13  | True                   |
| Chronos-2                |  21 |  -6.58824  | 4.45079e-11  | True                   |
| TimesFM 3.0              |  21 |  -6.23436  | 4.53627e-10  | True                   |
| XGBoost                  |  21 |  -0.486666 | 0.626495     | True                   |
| LightGBM                 |  21 |   0.170791 | 0.864388     | False                  |
| Hour-of-week climatology |  22 |   8.94347  | 3.7714e-19   | False                  |
| Timestral 28M            |  22 |  -7.32667  | 2.3595e-13   | True                   |
| Timestral 209M           |  22 |  -7.11359  | 1.1306e-12   | True                   |
| Chronos-2                |  22 |  -6.12236  | 9.22004e-10  | True                   |
| TimesFM 3.0              |  22 |  -4.76973  | 1.84469e-06  | True                   |
| LightGBM                 |  22 |   2.67157  | 0.00754963   | False                  |
| XGBoost                  |  22 |   1.92387  | 0.0543707    | False                  |
| Hour-of-week climatology |  23 |   8.29468  | 1.0888e-16   | False                  |
| Timestral 28M            |  23 |  -5.75071  | 8.88671e-09  | True                   |
| Timestral 209M           |  23 |  -5.20501  | 1.93981e-07  | True                   |
| Chronos-2                |  23 |  -4.13626  | 3.53017e-05  | True                   |
| TimesFM 3.0              |  23 |  -2.85223  | 0.00434139   | True                   |
| LightGBM                 |  23 |   1.49557  | 0.134767     | False                  |
| XGBoost                  |  23 |   1.32363  | 0.185625     | False                  |
| Hour-of-week climatology |  24 |   9.12514  | 7.16422e-20  | False                  |
| Timestral 28M            |  24 |  -5.89471  | 3.7533e-09   | True                   |
| Timestral 209M           |  24 |  -5.48723  | 4.08276e-08  | True                   |
| Chronos-2                |  24 |  -4.44323  | 8.86167e-06  | True                   |
| TimesFM 3.0              |  24 |  -3.67353  | 0.000239224  | True                   |
| LightGBM                 |  24 |  -0.901467 | 0.36734      | True                   |
| XGBoost                  |  24 |  -0.650253 | 0.515529     | True                   |