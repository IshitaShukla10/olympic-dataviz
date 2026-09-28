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

**`data/raw/gdp_pop_ref.csv`** and **`data/raw/flfp_ref.csv`** are
**placeholder figures for prototyping only** — approximate values assembled
from general knowledge, not pulled from an official release. They must be
replaced before the report is written. Real sources to use instead:

| Indicator | Source | Series code |
|---|---|---|
| GDP (nominal, current US$) | World Bank Open Data | `NY.GDP.MKTP.CD` |
| Population, total | World Bank Open Data | `SP.POP.TOTL` |
| Female labour-force participation rate (% ages 15+) | World Bank Open Data | `SL.TLF.CACT.FE.ZS` |

Download as CSV from https://data.worldbank.org/ (or the API at
`https://api.worldbank.org/v2/country/all/indicator/<code>?format=json`),
save into `data/raw/`, and update `scripts/clean_data.py`'s
`build_medals_total_with_econ()` / `build_female_medal_share_vs_flfp()` to
read the real files instead of the `*_ref.csv` placeholders.

## Country-name mismatches to watch for

Country naming is inconsistent across files and across eras (e.g. "Great
Britain" vs "United Kingdom", "People's Republic of China" vs "China", "100m
men" vs "Men's 100m" for event titles). Every join in `clean_data.py` that
needed this has an explicit name-mapping dict or a set of accepted variants —
check there first if a country/event silently drops out of a merge.
