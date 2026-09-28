# Project plan

## Story

**"Money Buys Medals — Equity Might Buy More"** — Paris 2024 through two
structural lenses (economic scale, gender equity) instead of a standard
medal-table tour.

## Structure (6-minute video, ~3 min per presenter)

| Section | Presenter | Time | Content |
|---|---|---|---|
| Title + intros | Both | 0:20 | Title card, both names, one-line hook |
| Act 1 — The economics of winning | A | 2:30 | GDP vs medals scatter (log-log) → pivot to over/under-performer residuals (who beats/misses their economic weight class) → host-nation medal-share boost |
| Act 2 — The equity dividend | B | 2:30 | Gender share of events over time (100% stacked bar, 1896->2024) → female labour-force participation vs female medal share scatter → medallist age by sport (violin) as a coda |
| Close | Both | 0:20 | Tie both acts: economic scale sets the ceiling, equity/strategy decide who reaches it |

## Chart taxonomy coverage (all 12 core types)

- Comparison: bar (medal leaders), line (winning-time trend)
- Composition: donut (individual vs team medals), stacked bar (medal source by
  country), 100% stacked bar (gender share of events), stacked area (events
  per Games by sport family — supporting/B-roll)
- Relationship: scatter x2 (GDP-medals, FLFP-medals), bubble (host boost
  before/home/after), heatmap (country x discipline specialisation)
- Distribution: histogram (medal-session timing — optional transition),
  box plot (gold/silver winning margin by decade), violin (age by sport)

## Novelty to name explicitly in the report

1. GDP-*residual* framing (who over/under-performs their economy) instead of
   the raw GDP-vs-medals scatter everyone runs on this dataset.
2. Female labour-force participation vs female medal share — an
   under-used pairing on this dataset; frames "who wins" against a country's
   off-the-field gender equity rather than just its wealth.
3. Host-boost-decay as a derived counterfactual metric (home Games vs the
   average of the Games immediately before/after), not a raw stat.

## Sensitivities to avoid

- No regime-type / political-system framing (brief explicitly bans
  social/cultural/political sensitivities in a publicly shared video).
- LA 1984 excluded from the host-boost chart — distorted by the Eastern-bloc
  boycott, not a genuine home-field effect, and boycotts are exactly the kind
  of politically loaded footnote to leave out of the narration.
- Frame medal comparisons neutrally ("most medals", not "dominance"); avoid
  GDP-per-capita national-pride framing.

## Timeline

| Week | Milestone |
|---|---|
| 1 | Clean + join data, confirm real (not placeholder) GDP/FLFP numbers, lock story |
| 2 | Style guide (palette, fonts, per-country colour), static drafts of all charts |
| 3 | Build animations/interactions, write + time the script (~420 words/presenter) |
| 4 | Record narration, edit, 720p legibility check |
| 5 | Write 2-page report, upload to YouTube labelled with group number, submit |

## Tooling

Plotly.js (CDN, no build step) for the interactive prototypes in `viz/`.
Screen-recorded for the video; final cut in DaVinci Resolve/CapCut.
