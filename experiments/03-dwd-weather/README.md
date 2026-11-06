# Experiment 03 — DWD station observations, hourly 2m air temperature

**Working title:** *AI vs. the weather station: who reads tomorrow's air?*

## Research question

Can zero-shot foundation models forecast hourly 2m air temperature at real
DWD stations — including heat spikes above a frozen P90 threshold — well
enough to beat seasonal-naive and GBMs? Temperature is the canonical
forecasting target: strong diurnal + annual cycle, weak exogenous signal.
An honest test of whether foundation priors beat local history.

## Dataset

[Deutscher Wetterdienst (DWD) Open Data](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/),
hourly air_temperature (TU) product, license CC BY 4.0, attribution
"Deutscher Wetterdienst", no API token. Per station we pull the historical
archive zip + the rolling recent zip and merge (recent rows win on overlap),
so each series ends at the last published hour.

30 stations, one per major German city, all 16 federal states covered,
longest available records among active stations. Benchmark window
2015-01 → present (config `data.start`). Missing = -999 → null; the
non-existent spring-forward hour is dropped; the repeated fall-back hour is
deduplicated to one Europe/Berlin instant.

| Station (city) | ID | State | Record from |
|---|---|---|---|
| Berlin-Tempelhof | 00433 | Berlin | 1951 |
| Hamburg-Fuhlsbuettel | 01975 | Schleswig-Holstein | 1949 |
| Muenchen-Flughafen | 01262 | Bayern | 1992 |
| Koeln-Bonn | 02667 | Nordrhein-Westfalen | 1960 |
| Frankfurt-Main | 01420 | Hessen | 1981 |
| Stuttgart-Schnarrenberg | 04928 | Baden-Wuerttemberg | 1977 |
| Duesseldorf | 01078 | Nordrhein-Westfalen | 1976 |
| Leipzig-Holzhausen | 02928 | Sachsen | 1951 |
| Dresden-Klotzsche | 01048 | Sachsen | 1973 |
| Bremen | 00691 | Bremen | 1949 |
| Hannover | 02014 | Niedersachsen | 1949 |
| Nuernberg | 03668 | Bayern | 1951 |
| Essen-Bredeney | 01303 | Nordrhein-Westfalen | 1951 |
| Braunschweig | 00662 | Niedersachsen | 1951 |
| Mannheim | 05906 | Baden-Wuerttemberg | 1948 |
| Freiburg | 01443 | Baden-Wuerttemberg | 1951 |
| Erfurt-Weimar | 01270 | Thueringen | 1951 |
| Rostock-Warnemuende | 04271 | Mecklenburg-Vorpommern | 1947 |
| Potsdam | 03987 | Brandenburg | 1893 |
| Magdeburg | 03126 | Sachsen-Anhalt | 1955 |
| Saarbruecken-Ensheim | 04336 | Saarland | 1962 |
| Trier-Petrisberg | 05100 | Rheinland-Pfalz | 1941 |
| Mainz-Lerchenberg | 03137 | Rheinland-Pfalz | 2008 |
| Kiel-Holtenau | 02564 | Schleswig-Holstein | 2002 |
| Schwerin | 04625 | Mecklenburg-Vorpommern | 1950 |
| Cottbus | 00880 | Brandenburg | 1956 |
| Regensburg | 04104 | Bayern | 1948 |
| Wuerzburg | 05705 | Bayern | 1948 |
| Goerlitz | 01684 | Sachsen | 1951 |
| Konstanz | 02712 | Baden-Wuerttemberg | 1971 |

## Protocol

- Forecast origin = **00:00 local (Europe/Berlin) on day D**, daily cadence
  (`origin_step_hours: 24`); information set = everything strictly before
  the origin.
- Targets: the next 24 wall-clock hours of D; `h` = 1..24.
- `min_train_hours: 17520` (2 years) before the first origin.
- Heat-day threshold: training-period P90 of the series, frozen before
  holdout (config `events.train_quantile: 0.9`).
- Series ids: `air_temperature/<station_id>` (zero-padded DWD id).

## Results

In `results/` — verified numbers only in the technical report (once run).

## Reproduce

```bash
uv sync --group dev --extra ml --extra foundation
uv run arena build-data 03
uv run --extra ml --extra foundation arena run 03 --tier smoke
uv run --extra ml --extra foundation arena run 03 --tier pilot
uv run --extra ml --extra foundation arena run 03 --tier full
```

## Limitations

- Station local-time timestamps: the fall-back duplicate hour and the
  missing spring-forward hour are inherent to DWD legal-time data.
- Sensor drift/relocation: long series mix instrument generations; no
  homogenization applied (raw observations, as published).
- Raw gaps (sensor downtime, -999) stay NaN on the union grid; models get
  hour-of-week imputation only.
