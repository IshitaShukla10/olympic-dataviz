# Money Buys Medals — Equity Might Buy More

SC4024 Data Visualisation project. A Paris 2024 / 128-year Olympics story told
through two structural lenses — economic scale and gender equity — instead of
the usual medal-table tour.

See [`docs/PLAN.md`](docs/PLAN.md) for the full project plan (story, chart
list, novelty angle, timeline) and [`docs/DATASETS.md`](docs/DATASETS.md) for
what every data file is and where it comes from.

## Status

Early build: data cleaning pipeline is working, and the first two interactive
chart prototypes are done. See `viz/` and open the `.html` files directly in
a browser.

- [x] Data cleaning pipeline (`scripts/clean_data.py`)
- [x] Prototype: sprint/marathon winning-time trend (line chart)
- [x] Prototype: host-nation medal-share boost (grouped bar)
- [ ] 100% stacked bar — gender share of events over time
- [ ] Heatmap — country x discipline medal specialisation
- [ ] Scatter — GDP vs medals, with over/under-performer highlighting
- [ ] Scatter — female labour-force participation vs female medal share
- [ ] Violin — medallist age by sport
- [ ] Donut — individual vs team medal split
- [ ] Box plot — gold/silver winning-margin by decade
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
