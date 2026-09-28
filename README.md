# Money Buys Medals — Equity Might Buy More

SC4024 Data Visualisation project. A Paris 2024 / 128-year Olympics story told
through two structural lenses — economic scale and gender equity — instead of
the usual medal-table tour.

See [`docs/PLAN.md`](docs/PLAN.md) for the full project plan (story, chart
list, novelty angle, timeline) and [`docs/DATASETS.md`](docs/DATASETS.md) for
what every data file is and where it comes from.

## Status

All 12 taxonomy charts have a working interactive prototype in `viz/` —
open `viz/index.html` for the full list. GDP and population are real World
Bank data; female labour-force participation is still a placeholder (see
`docs/DATASETS.md`).

- [x] Data cleaning pipeline (`scripts/clean_data.py`)
- [x] Real World Bank GDP + population data (was placeholder)
- [x] All 10 prototype charts built (line, grouped bar, 100% stacked bar,
      heatmap, 2x scatter, violin, donut, box plot, stacked bar — covers
      all 12 taxonomy chart types across the two-act story)
- [ ] Replace female labour-force participation placeholder with real
      World Bank `SL.TLF.CACT.FE.ZS` data (see `docs/DATASETS.md`)
- [ ] Style pass — one consistent palette/typography across all charts,
      legible at 720p
- [ ] Script + storyboard, timed to 3 min/presenter
- [ ] Recording, editing, final export at <=720p

## Repo layout

```
data/
  raw/     source CSVs + the results pickle (gitignored — see below)
  clean/   small, chart-ready CSVs produced by scripts/clean_data.py
scripts/
  clean_data.py   builds everything in data/clean/ from data/raw/
  build_viz.py    generates the interactive chart prototypes in viz/
viz/       self-contained HTML charts (Plotly.js via CDN, data embedded inline)
docs/
  PLAN.md       the project plan
  DATASETS.md   data dictionary + sourcing notes, incl. what's still a placeholder
```

## Setup

```bash
pip install pandas numpy
```

The raw Kaggle "Paris 2024 Olympic Summer Games" dataset (and the historical
`olympic_results.pkl`) is not committed to the repo — it's ~45MB and freely
re-downloadable. Put the original files in `data/raw/`, then:

```bash
python3 scripts/clean_data.py   # -> data/clean/*.csv
python3 scripts/build_viz.py    # -> viz/*.html
```

Open any file in `viz/` directly in a browser — no server needed.

## A note on the economic/social reference data

`data/raw/gdp_pop_ref.csv` and `data/raw/flfp_ref.csv` are **placeholder**
figures for early prototyping, not sourced from an official release yet.
Before anything using them goes in the final report, swap them for the real
World Bank indicators — see `docs/DATASETS.md` for exact series codes.
