# Datasets

## Core Olympics data (Kaggle: "Paris 2024 Olympic Summer Games" dataset)

Download the original zip and place the CSVs + `olympic_results.pkl` in
`data/raw/` (gitignored — see `README.md`).

| File | Rows | Used for |
|---|---|---|
| `olympic_results.pkl` | 162,904 | 1896-2022 historical results (all disciplines). Source for the winning-time trend, gender-share-over-time, and host-boost charts. |
| `olympic_hosts.csv` | 53 | Games metadata: year, season, host location. Joined onto `olympic_results.pkl` by `slug_game`/`game_slug`. |
| `medals_total_2024.csv` | 92 countries | Paris 2024 medal counts by country. Base table for the GDP-residual chart. |
| `medals_2024.csv` | 1,044 | Paris 2024 medals, one row per medal (team medals collapsed to one row). |
| `medallists_2024.csv` | 2,315 | Paris 2024 medals, one row per athlete (team medals expanded). Source for age-by-sport and female-medal-share. |
| `teams_2024.csv` | 1,698 | Paris 2024 team rosters by discipline/gender. Supporting context for squad-size charts. |
| `olympic_athletes.csv` | 456,890 | All-time athlete index (career span, birth year). Supporting context only; not yet used in a clean output. |

Other files in the raw zip (`coaches_2024.csv`, `technical_officials_2024.csv`,
`nocs_2024.csv`, `schedules_2024.csv`, `schedules_preliminary_2024.csv`,
`torch_route_2024.csv`, `venues_2024.csv`, `events_2024.csv`) are kept in
`data/raw/` for the schedule-replay / torch-route chart planned for later but
not yet processed by `clean_data.py`.

## Reference data — economic & social indicators

| File | Status | Source |
|---|---|---|
| `data/raw/wb_gdp_raw.csv` | **Real data** | World Bank `NY.GDP.MKTP.CD` (GDP, current US$), via the [datasets/gdp](https://github.com/datasets/gdp) mirror, 1960-2023 |
| `data/raw/wb_population_raw.csv` | **Real data** | World Bank `SP.POP.TOTL` (total population), via the [datasets/population](https://github.com/datasets/population) mirror, 1960-2023 |
| `data/raw/flfp_ref.csv` | **Placeholder — still needs replacing** | Approximate values from general knowledge, not an official release |

`build_medals_total_with_econ()` in `scripts/clean_data.py` uses the latest
available year per country (mostly 2023) from the two real World Bank files
above, joined onto `medals_total_2024.csv` via the `PARIS_TO_WB_NAME` mapping
(World Bank naming differs from the Olympics dataset's, e.g. "Korea, Rep."
vs "Korea", "Turkiye" vs "Türkiye").

**Countries dropped from `medals_total_with_econ.csv`** (no World Bank
match): `AIN` and `EOR` (not countries — neutral/refugee teams), `Chinese
Taipei` (Taiwan is excluded from the World Bank's country classifications
entirely), `DPR Korea` (population data exists but GDP is not reported), and
`Puerto Rico` (US territory, not separately listed). 87 of 92 Paris 2024
medal-winning countries/teams are covered.

**Female labour-force participation is still a placeholder.** No reachable
mirror for World Bank `SL.TLF.CACT.FE.ZS` was found from this environment
(data.worldbank.org, the World Bank API, and datahub.io are all network-
blocked here). To fix it: download the indicator as CSV yourself from
https://data.worldbank.org/indicator/SL.TLF.CACT.FE.ZS, save it as
`data/raw/wb_flfp_raw.csv` in the same `Country Name, Country Code, Year,
Value` shape as the GDP/population files, and update
`build_female_medal_share_vs_flfp()` in `scripts/clean_data.py` to read it
(mirror the `_latest_wb_value()` / `PARIS_TO_WB_NAME` pattern already used
for GDP).

## Country-name mismatches to watch for

Country naming is inconsistent across files and across eras (e.g. "Great
Britain" vs "United Kingdom", "People's Republic of China" vs "China", "100m
men" vs "Men's 100m" for event titles). Every join in `clean_data.py` that
needed this has an explicit name-mapping dict or a set of accepted variants —
check there first if a country/event silently drops out of a merge.
