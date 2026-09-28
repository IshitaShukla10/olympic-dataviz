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
    data_json = json.dumps(
        {
            "country": df.country.tolist(),
            "prior": df.prior_share.tolist(),
            "home": df.home_share.tolist(),
            "next": df.next_share.tolist(),
        }
    )
    chart_js = """
const traces = [
  { x: data.country, y: data.prior.map(v => v*100), name: 'Games before', type: 'bar', marker:{color:'#3b4252'} },
  { x: data.country, y: data.home.map(v => v*100),  name: 'Home Games',   type: 'bar', marker:{color:'#ff922b'} },
  { x: data.country, y: data.next.map(v => v*100),  name: 'Games after',  type: 'bar', marker:{color:'#3b4252'} },
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


if __name__ == "__main__":
    build_sprint_trend_chart()
    build_host_boost_chart()
