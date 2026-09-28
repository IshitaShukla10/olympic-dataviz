"""
Generates the first two self-contained, interactive prototype charts from
the cleaned CSVs in data/clean/, using Plotly.js via CDN. Each chart is a
single HTML file that can be opened directly in a browser (data is embedded
inline as JSON, so there is no CORS/file:// issue and nothing else to serve).

Run after scripts/clean_data.py:
    python3 scripts/build_viz.py
"""
import json
import pandas as pd
from pathlib import Path

CLEAN = Path(__file__).resolve().parent.parent / "data" / "clean"
VIZ = Path(__file__).resolve().parent.parent / "viz"
VIZ.mkdir(parents=True, exist_ok=True)

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2/plotly.min.js"></script>
<style>
  body {{ margin:0; font-family:-apple-system,Segoe UI,Roboto,sans-serif; background:#0b0e14; color:#e8ecf1; }}
  header {{ padding:20px 24px 4px; }}
  h1 {{ font-size:1.3rem; margin:0 0 4px; }}
  p.sub {{ margin:0; color:#9aa4b2; font-size:0.95rem; max-width:760px; }}
  #chart {{ width:100%; height:640px; }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
</header>
<div id="chart"></div>
<script>
const data = {data_json};
{chart_js}
</script>
</body>
</html>
"""


def write_page(filename, title, subtitle, data_json, chart_js):
    html = PAGE_TEMPLATE.format(
        title=title, subtitle=subtitle, data_json=data_json, chart_js=chart_js
    )
    (VIZ / filename).write_text(html, encoding="utf-8")
    print("wrote", VIZ / filename)


def build_sprint_trend_chart():
    df = pd.read_csv(CLEAN / "sprint_trend.csv")
    traces = []
    colors = {"100m Men": "#ff6b6b", "100m Women": "#4dabf7", "Marathon Men": "#ffd43b"}
    for event, sub in df.groupby("event"):
        sub = sub.sort_values("game_year")
        # Marathon is on a different scale (seconds over ~2h vs ~10s), so it
        # gets its own y-axis via a dropdown toggle rather than one shared axis.
        traces.append(
            {
                "x": sub.game_year.tolist(),
                "y": sub.seconds.tolist(),
                "text": sub.athlete_full_name.tolist(),
                "customdata": sub.country_name.tolist(),
                "name": event,
                "mode": "lines+markers",
                "line": {"width": 3, "color": colors.get(event, "#aaa")},
                "hovertemplate": "%{x}: %{text} (%{customdata})<br>%{y:.2f}s<extra>%{fullData.name}</extra>",
                "visible": True if event != "Marathon Men" else False,
            }
        )
    data_json = json.dumps(traces)
    chart_js = """
const sprintTraces = data.filter(d => d.name !== 'Marathon Men');
const marathonTrace = data.find(d => d.name === 'Marathon Men');

function render(showMarathon) {
  const traces = showMarathon ? [marathonTrace] : sprintTraces;
  Plotly.newPlot('chart', traces.map(t => ({...t, visible: true})), {
    paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
    font: { color: '#e8ecf1', size: 14 },
    xaxis: { title: 'Olympic Games (year)', gridcolor: '#222' },
    yaxis: { title: showMarathon ? 'Winning time (seconds, lower = faster)' : 'Winning time (seconds)', gridcolor: '#222' },
    legend: { orientation: 'h', y: -0.15 },
    margin: { t: 20 },
    updatemenus: [{
      buttons: [
        { label: '100m Sprints', method: 'skip' },
        { label: 'Marathon', method: 'skip' }
      ],
      direction: 'left', x: 0, y: 1.12, showactive: true
    }]
  }, {responsive: true});
}
render(false);

document.getElementById('chart').addEventListener('plotly_relayout', () => {});
// simple toggle buttons injected above the chart
const toggle = document.createElement('div');
toggle.style.padding = '0 24px 12px';
toggle.innerHTML = `
  <button id="btn-sprint" style="margin-right:8px;padding:6px 14px;border-radius:6px;border:1px solid #444;background:#1a1f29;color:#e8ecf1;cursor:pointer;">100m Sprints</button>
  <button id="btn-marathon" style="padding:6px 14px;border-radius:6px;border:1px solid #444;background:#1a1f29;color:#e8ecf1;cursor:pointer;">Marathon</button>
`;
document.querySelector('header').after(toggle);
document.getElementById('btn-sprint').onclick = () => render(false);
document.getElementById('btn-marathon').onclick = () => render(true);
"""
    write_page(
        "01_sprint_trend.html",
        "Are Olympic winners still getting faster?",
        "Men's & women's 100m and men's marathon winning times, 1896-2016 (Athletics discipline, gold medallists only). "
        "Toggle between sprint and endurance events -- note the flattening curve since the 1990s.",
        data_json,
        chart_js,
    )


def build_host_boost_chart():
    df = pd.read_csv(CLEAN / "host_boost.csv")
    df = df.sort_values("home_share", ascending=False)
    # Tokyo 2020's "next" Games (Paris 2024) isn't in olympic_hosts.csv, so
    # that cell is legitimately missing -- serialize as JSON null, not NaN
    # (NaN is not valid JSON and breaks JS parsing).
    to_list = lambda s: [None if pd.isna(v) else v for v in s]
    data_json = json.dumps(
        {
            "country": df.country.tolist(),
            "prior": to_list(df.prior_share),
            "home": to_list(df.home_share),
            "next": to_list(df.next_share),
        }
    )
    chart_js = """
const pct = v => v == null ? null : v * 100;  // preserve gaps for missing data (e.g. Tokyo's "next" Games isn't in the dataset) instead of drawing a false zero
const traces = [
  { x: data.country, y: data.prior.map(pct), name: 'Games before', type: 'bar', marker:{color:'#3b4252'} },
  { x: data.country, y: data.home.map(pct),  name: 'Home Games',   type: 'bar', marker:{color:'#ff922b'} },
  { x: data.country, y: data.next.map(pct),  name: 'Games after',  type: 'bar', marker:{color:'#3b4252'} },
];
Plotly.newPlot('chart', traces, {
  barmode: 'group',
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 14 },
  yaxis: { title: 'Share of all medals at that Games (%)', gridcolor: '#222' },
  legend: { orientation: 'h', y: -0.2 },
  margin: { t: 20 },
}, {responsive: true});
"""
    write_page(
        "02_host_boost.html",
        "The home-field advantage, quantified",
        "Each host nation's share of total medals at its own Games, compared to the Games immediately before and after "
        "(same season). Every host jumps at home, then mostly reverts. (1984 Los Angeles excluded: distorted by the "
        "Eastern-bloc boycott, not a genuine home effect.)",
        data_json,
        chart_js,
    )


def build_gender_share_chart():
    df = pd.read_csv(CLEAN / "gender_share_by_games.csv")
    df = df[df.game_season == "Summer"]  # one continuous series reads cleaner than interleaving both seasons
    piv = df.pivot_table(index="game_year", columns="gender_cat", values="share", fill_value=0).reset_index()
    for col in ["Men", "Women", "Mixed / Open"]:
        if col not in piv:
            piv[col] = 0
    data_json = json.dumps(
        {
            "year": piv.game_year.tolist(),
            "men": (piv["Men"] * 100).tolist(),
            "women": (piv["Women"] * 100).tolist(),
            "mixed": (piv["Mixed / Open"] * 100).tolist(),
        }
    )
    chart_js = """
const traces = [
  { x: data.year, y: data.women, name: 'Women', type: 'bar', marker: {color:'#e64980'} },
  { x: data.year, y: data.mixed, name: 'Mixed / Open', type: 'bar', marker: {color:'#868e96'} },
  { x: data.year, y: data.men,   name: 'Men',   type: 'bar', marker: {color:'#4dabf7'} },
];
Plotly.newPlot('chart', traces, {
  barmode: 'stack',
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 14 },
  xaxis: { title: 'Summer Games (year)', gridcolor: '#222' },
  yaxis: { title: 'Share of results (%)', range: [0,100], gridcolor: '#222' },
  shapes: [{type:'line', x0:1896, x1:2020, y0:50, y1:50, line:{color:'#ffd43b', width:1, dash:'dot'}}],
  legend: { orientation: 'h', y: -0.15 },
  margin: { t: 20 },
}, {responsive: true});
"""
    write_page(
        "03_gender_share.html",
        "128 years toward parity",
        "Share of Summer Games results that are women's, men's, or mixed/open events, 1896-2020. Dotted line marks 50%.",
        data_json,
        chart_js,
    )


def build_heatmap_chart():
    df = pd.read_csv(CLEAN / "country_discipline_heatmap.csv")
    countries = df.groupby("country").n.sum().sort_values(ascending=False).index.tolist()
    disciplines = df.groupby("discipline").n.sum().sort_values(ascending=False).head(14).index.tolist()
    df = df[df.discipline.isin(disciplines)]
    piv = df.pivot_table(index="country", columns="discipline", values="n", fill_value=0)
    piv = piv.reindex(countries)[disciplines]
    data_json = json.dumps(
        {"z": piv.values.tolist(), "countries": piv.index.tolist(), "disciplines": piv.columns.tolist()}
    )
    chart_js = """
Plotly.newPlot('chart', [{
  z: data.z, x: data.disciplines, y: data.countries, type: 'heatmap',
  colorscale: [[0,'#0b0e14'],[0.15,'#1c3a52'],[0.5,'#1c7ed6'],[1,'#ffd43b']],
  hovertemplate: '%{y} - %{x}: %{z} medals<extra></extra>',
  colorbar: { title: 'Medals' }
}], {
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 12 },
  xaxis: { tickangle: -40 },
  yaxis: { autorange: 'reversed' },
  margin: { t: 20, l: 140, b: 120 },
}, {responsive: true});
"""
    write_page(
        "04_country_discipline_heatmap.html",
        "Where each country's medals come from",
        "Top 15 Paris 2024 medal-winning countries x their strongest disciplines. Rows sorted by total medals; look for the "
        "bright single-column countries (specialists) vs. the spread-out rows (broad programmes).",
        data_json,
        chart_js,
    )


def build_gdp_residual_chart():
    df = pd.read_csv(CLEAN / "medals_total_with_econ.csv")
    df = df[df.Total > 0].copy()
    import numpy as np

    x = np.log(df.gdp_usd_billion)
    y = np.log(df.Total)
    slope, intercept = np.polyfit(x, y, 1)
    df["predicted"] = np.exp(slope * x + intercept)
    df["resid"] = np.log(df.Total) - np.log(df.predicted)
    df["category"] = pd.cut(
        df.resid, bins=[-10, -0.6, 0.6, 10], labels=["Under-performs GDP", "In line with GDP", "Over-performs GDP"]
    )
    colors = {"Over-performs GDP": "#40c057", "In line with GDP": "#868e96", "Under-performs GDP": "#fa5252"}
    xs_line = [df.gdp_usd_billion.min(), df.gdp_usd_billion.max()]
    ys_line = [float(np.exp(slope * np.log(v) + intercept)) for v in xs_line]

    traces = []
    for cat, sub in df.groupby("category", observed=True):
        traces.append(
            {
                "x": sub.gdp_usd_billion.tolist(),
                "y": sub.Total.tolist(),
                "text": sub.country.tolist(),
                "mode": "markers",
                "type": "scatter",
                "name": cat,
                "marker": {"color": colors[cat], "size": 10, "line": {"width": 1, "color": "#0b0e14"}},
                "hovertemplate": "%{text}<br>GDP $%{x:.0f}B, %{y} medals<extra>%{fullData.name}</extra>",
            }
        )
    traces.append(
        {
            "x": xs_line, "y": ys_line, "mode": "lines", "type": "scatter", "name": "GDP-predicted trend",
            "line": {"color": "#495057", "dash": "dash"}, "hoverinfo": "skip",
        }
    )
    data_json = json.dumps(traces)
    chart_js = """
Plotly.newPlot('chart', data, {
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 14 },
  xaxis: { title: 'GDP (current US$, billions)', type: 'log', gridcolor: '#222' },
  yaxis: { title: 'Paris 2024 total medals', type: 'log', gridcolor: '#222' },
  legend: { orientation: 'h', y: -0.2 },
  margin: { t: 20 },
}, {responsive: true});
"""
    write_page(
        "05_gdp_residual_scatter.html",
        "Money buys medals -- with steep diminishing returns",
        "GDP vs. Paris 2024 medal count (log-log; source: World Bank NY.GDP.MKTP.CD). Colour marks who over/under-performs "
        "their economy's predicted medal count, not just the raw scatter everyone runs on this dataset.",
        data_json,
        chart_js,
    )


def build_flfp_scatter_chart():
    df = pd.read_csv(CLEAN / "flfp_vs_medal_share.csv")
    import numpy as np

    slope, intercept = np.polyfit(df.flfp_pct, df.female_medal_share, 1)
    xs_line = [df.flfp_pct.min(), df.flfp_pct.max()]
    ys_line = [slope * v + intercept for v in xs_line]
    data_json = json.dumps(
        {
            "x": df.flfp_pct.tolist(),
            "y": (df.female_medal_share * 100).tolist(),
            "text": df.country.tolist(),
            "size": df.n_medallists.tolist(),
            "line_x": xs_line,
            "line_y": [v * 100 for v in ys_line],
        }
    )
    chart_js = """
Plotly.newPlot('chart', [
  {
    x: data.x, y: data.y, text: data.text, mode: 'markers+text', type: 'scatter',
    textposition: 'top center', textfont: {size:10, color:'#9aa4b2'},
    marker: { size: data.size, sizeref: Math.max(...data.size)/900, sizemin:6, color:'#4dabf7', line:{width:1,color:'#0b0e14'} },
    hovertemplate: '%{text}<br>FLFP %{x}%%, %{y:.0f}%% of medals won by women<extra></extra>',
    name: 'Country'
  },
  { x: data.line_x, y: data.line_y, mode:'lines', type:'scatter', line:{color:'#495057',dash:'dash'}, name:'Trend', hoverinfo:'skip' }
], {
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 14 },
  xaxis: { title: 'Female labour-force participation rate (%)', gridcolor: '#222' },
  yaxis: { title: "Share of country's medals won by women (%)", gridcolor: '#222' },
  showlegend: false,
  margin: { t: 20 },
}, {responsive: true});
"""
    write_page(
        "06_flfp_vs_medal_share.html",
        "The equity dividend",
        "PLACEHOLDER DATA -- flfp_ref.csv is not yet sourced from World Bank SL.TLF.CACT.FE.ZS, see docs/DATASETS.md. "
        "Female labour-force participation rate vs. each country's share of Paris 2024 medals won by women "
        "(countries with >=5 medallists). Bubble size = number of medallists.",
        data_json,
        chart_js,
    )


def build_age_violin_chart():
    df = pd.read_csv(CLEAN / "age_by_sport.csv")
    top = df.discipline.value_counts().head(12).index.tolist()
    df = df[df.discipline.isin(top)]
    order = df.groupby("discipline").age.median().sort_values().index.tolist()
    traces = []
    for disc in order:
        sub = df[df.discipline == disc]
        traces.append({"y": sub.age.round(1).tolist(), "type": "violin", "name": disc, "box": {"visible": True}, "meanline": {"visible": True}, "points": False})
    data_json = json.dumps(traces)
    chart_js = """
Plotly.newPlot('chart', data.map(t => ({...t, line:{color:'#4dabf7'}, fillcolor:'rgba(77,171,247,0.3)'})), {
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 13 },
  xaxis: { tickangle: -30 },
  yaxis: { title: 'Medallist age (years)', gridcolor: '#222' },
  showlegend: false,
  margin: { t: 20, b: 110 },
}, {responsive: true});
"""
    write_page(
        "07_age_by_sport_violin.html",
        "How old is an Olympic champion?",
        "Age distribution of Paris 2024 medallists, top 12 disciplines by medallist count, sorted youngest to oldest median.",
        data_json,
        chart_js,
    )


def build_medal_type_donut():
    df = pd.read_csv(CLEAN / "medal_type_split.csv")
    data_json = json.dumps({"labels": df.category.tolist(), "values": df.n_medallists.tolist()})
    chart_js = """
Plotly.newPlot('chart', [{
  labels: data.labels, values: data.values, type: 'pie', hole: 0.55,
  marker: { colors: ['#4dabf7', '#ffd43b', '#868e96'] },
  textinfo: 'label+percent', hovertemplate: '%{label}: %{value} medallists<extra></extra>'
}], {
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 14 },
  showlegend: false,
  margin: { t: 20 },
}, {responsive: true});
"""
    write_page(
        "08_medal_type_donut.html",
        "Individual, pairs, or team?",
        "Paris 2024 medallists by event type. 'Individual' includes head-to-head sports like judo and boxing.",
        data_json,
        chart_js,
    )


def build_winning_margin_box():
    df = pd.read_csv(CLEAN / "winning_margin.csv")
    df = df[df.decade >= 1950]  # sparse before 1950
    decades = sorted(df.decade.unique())
    data_json = json.dumps(
        {
            "decade": df.decade.tolist(),
            "margin": df.margin_pct.tolist(),
        }
    )
    chart_js = """
Plotly.newPlot('chart', [{
  x: data.decade, y: data.margin, type: 'box',
  marker: { color: '#4dabf7' }, boxpoints: 'outliers'
}], {
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 14 },
  xaxis: { title: 'Decade', dtick: 10, gridcolor: '#222' },
  yaxis: { title: 'Gold-silver winning margin (% of winning time)', type: 'log', gridcolor: '#222' },
  margin: { t: 20 },
}, {responsive: true});
"""
    write_page(
        "09_winning_margin_box.html",
        "Is the gap between gold and silver shrinking?",
        "Gold-to-silver winning margin as a % of the winning time, all timed events (Athletics, Swimming, etc.), by decade "
        "since 1950. Log y-axis: note how the whole distribution compresses toward zero.",
        data_json,
        chart_js,
    )


def build_medal_source_stacked_bar():
    df = pd.read_csv(CLEAN / "country_discipline_heatmap.csv")
    top_countries = df.groupby("country").n.sum().sort_values(ascending=False).head(6).index.tolist()
    sub = df[df.country.isin(top_countries)]
    top_disciplines = sub.groupby("discipline").n.sum().sort_values(ascending=False).head(8).index.tolist()
    sub = sub[sub.discipline.isin(top_disciplines)].copy()
    sub["discipline"] = sub.discipline.where(sub.discipline.isin(top_disciplines), "Other")
    traces_data = {}
    for disc in top_disciplines:
        d = sub[sub.discipline == disc].set_index("country").reindex(top_countries).n.fillna(0)
        traces_data[disc] = d.tolist()
    data_json = json.dumps({"countries": top_countries, "series": traces_data})
    chart_js = """
const palette = ['#4dabf7','#ffd43b','#e64980','#40c057','#fa5252','#845ef7','#22b8cf','#ff922b'];
const traces = Object.keys(data.series).map((disc, i) => ({
  x: data.countries, y: data.series[disc], name: disc, type: 'bar',
  marker: { color: palette[i % palette.length] }
}));
Plotly.newPlot('chart', traces, {
  barmode: 'stack',
  paper_bgcolor: '#0b0e14', plot_bgcolor: '#0b0e14',
  font: { color: '#e8ecf1', size: 14 },
  yaxis: { title: 'Medals', gridcolor: '#222' },
  legend: { orientation: 'h', y: -0.15 },
  margin: { t: 20 },
}, {responsive: true});
"""
    write_page(
        "10_medal_source_stacked_bar.html",
        "How the top 6 nations built their medal count",
        "Top 6 Paris 2024 medal-winning countries, broken down by their top 8 disciplines. Hover a segment to see the exact count.",
        data_json,
        chart_js,
    )


if __name__ == "__main__":
    build_sprint_trend_chart()
    build_host_boost_chart()
    build_gender_share_chart()
    build_heatmap_chart()
    build_gdp_residual_chart()
    build_flfp_scatter_chart()
    build_age_violin_chart()
    build_medal_type_donut()
    build_winning_margin_box()
    build_medal_source_stacked_bar()
