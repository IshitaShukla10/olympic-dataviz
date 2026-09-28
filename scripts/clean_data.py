"""
Data cleaning pipeline for the SC4024 Olympics data visualisation project.

Reads the raw Kaggle "Olympic dataset" (Paris 2024 + 1896-2022 historical
results) from data/raw/ and writes small, chart-ready CSVs to data/clean/.

Run:
    python3 scripts/clean_data.py

Requires: pandas, numpy
"""
import re
import numpy as np
import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CLEAN = Path(__file__).resolve().parent.parent / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)


def load_results():
    r = pd.read_pickle(RAW / "olympic_results.pkl")
    h = pd.read_csv(RAW / "olympic_hosts.csv")
    r = r.merge(
        h[["game_slug", "game_year", "game_season", "game_location"]],
        left_on="slug_game",
        right_on="game_slug",
        how="left",
    )
    return r, h


def parse_time_value(raw, unit):
    """value_unit for TIME events is stored as a zero-padded string encoding
    hours/minutes/seconds/hundredths, e.g. '9920' -> 9.92s for a sprint,
    '3045600' -> longer track/road events. We only need a handful of single
    flat-out sprint/endurance events for the line chart, so we parse those
    explicitly rather than guess a generic rule for all 43k TIME rows."""
    if pd.isna(raw):
        return np.nan
    s = str(raw).strip()
    if not s.isdigit():
        return np.nan
    s = s.zfill(6)
    hh, mm, ss_hh = s[:-4], s[-4:-2], s[-2:]
    try:
        return int(hh) * 3600 + int(mm) * 60 + int(ss_hh) / 100 * 1  # noqa
    except ValueError:
        return np.nan


def build_sprint_trend(r):
    """Winning time trend for a couple of flagship track events."""
    rows = []
    # event_title spelling changed across eras (e.g. "100m men" in older
    # Games vs "Men's 100m" from Rio onward), so match on a set of known
    # variants per event rather than a single exact string.
    targets = {
        "100m Men": ("Athletics", {"100m men", "men's 100m"}),
        "100m Women": ("Athletics", {"100m women", "women's 100m"}),
        "Marathon Men": ("Athletics", {"marathon men", "men's marathon"}),
    }
    for label, (disc, variants) in targets.items():
        sub = r[
            (r.discipline_title == disc)
            & (r.event_title.str.lower().isin(variants))
            & (r.medal_type == "GOLD")
        ].copy()
        if sub.empty:
            continue
        # value_unit for sprints is hundredths of a second as an integer
        # string (e.g. '9920' == 9.92s); parse defensively.
        def to_seconds(v):
            try:
                v = float(v)
            except (TypeError, ValueError):
                return np.nan
            return v / 100.0

        sub["seconds"] = sub.value_unit.apply(to_seconds)
        sub = sub.dropna(subset=["seconds", "game_year"])
        sub = sub[["game_year", "athlete_full_name", "country_name", "seconds"]]
        sub.insert(0, "event", label)
        rows.append(sub.sort_values("game_year"))
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    out.to_csv(CLEAN / "sprint_trend.csv", index=False)
    return out


def build_gender_share(r):
    """Share of results that are women's / men's / mixed events, by Games."""
    def classify(title):
        t = str(title).lower()
        if "women" in t:
            return "Women"
        if "men" in t:
            return "Men"
        return "Mixed / Open"

    r = r.copy()
    r["gender_cat"] = r.event_title.apply(classify)
    tab = (
        r.groupby(["game_year", "game_season", "gender_cat"])
        .size()
        .reset_index(name="n")
    )
    tot = tab.groupby(["game_year", "game_season"])["n"].transform("sum")
    tab["share"] = tab["n"] / tot
    tab.to_csv(CLEAN / "gender_share_by_games.csv", index=False)
    return tab


def build_host_boost(r, h):
    """Host country's share of medals at their own Games vs the Games
    immediately before and after (same season), for host nations with a
    reasonably unambiguous historical name match."""
    host_country_map = {
        "london-2012": "Great Britain",
        "rio-2016": "Brazil",
        "sydney-2000": "Australia",
        "beijing-2008": "People's Republic of China",
        "barcelona-1992": "Spain",
        "seoul-1988": "Republic of Korea",
        "atlanta-1996": "United States of America",
        "tokyo-2020": "Japan",
    }
    med = r[r.medal_type.notna()]
    rows = []
    for slug, name in host_country_map.items():
        season = h.loc[h.game_slug == slug, "game_season"].iloc[0]
        same = h[h.game_season == season].sort_values("game_year").reset_index(drop=True)
        idx = same.index[same.game_slug == slug][0]
        prior = same.game_slug.iloc[idx - 1] if idx >= 1 else None
        nxt = same.game_slug.iloc[idx + 1] if idx + 1 < len(same) else None

        def share(s):
            if s is None:
                return np.nan
            tot = med[med.slug_game == s].shape[0]
            home = med[(med.slug_game == s) & (med.country_name == name)].shape[0]
            return home / tot if tot else np.nan

        rows.append(
            {
                "host_slug": slug,
                "country": name,
                "prior_share": share(prior),
                "home_share": share(slug),
                "next_share": share(nxt),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(CLEAN / "host_boost.csv", index=False)
    return out


def build_age_by_sport():
    m = pd.read_csv(RAW / "medallists_2024.csv", parse_dates=["birth_date"])
    ref_date = pd.Timestamp("2024-08-01")
    m["age"] = (ref_date - m.birth_date).dt.days / 365.25
    m = m.dropna(subset=["age"])
    out = m[["discipline", "gender", "age", "country"]]
    out.to_csv(CLEAN / "age_by_sport.csv", index=False)
    return out


def build_medal_type_split():
    m = pd.read_csv(RAW / "medallists_2024.csv")
    tab = m.event_type.value_counts().reset_index()
    tab.columns = ["event_type", "n_medallists"]
    tab.to_csv(CLEAN / "medal_type_split.csv", index=False)
    return tab


def build_medals_total_with_econ():
    """Joins Paris 2024 medal totals with an economic reference table.

    IMPORTANT: data/raw/gdp_pop_ref.csv and flfp_ref.csv are APPROXIMATE
    figures assembled from general knowledge for early prototyping only.
    Before this goes in the report, replace them with the real World Bank
    indicators (NY.GDP.MKTP.CD, SP.POP.TOTL, SL.TLF.CACT.FE.ZS) -- see
    docs/PLAN.md for the exact series to pull.
    """
    mt = pd.read_csv(RAW / "medals_total_2024.csv")
    ref = pd.read_csv(RAW / "gdp_pop_ref.csv")
    name_fix = {"Hong Kong, China": "Hong Kong"}
    mt["ref_name"] = mt.country.map(lambda x: name_fix.get(x, x))
    df = mt.merge(ref, left_on="ref_name", right_on="country", how="left", suffixes=("", "_ref"))
    df = df.dropna(subset=["gdp_usd_billion", "population_million"])
    df["gdp_per_capita_usd"] = df.gdp_usd_billion * 1e3 / df.population_million
    df["medals_per_million"] = df.Total / df.population_million
    df.to_csv(CLEAN / "medals_total_with_econ.csv", index=False)
    return df


def build_female_medal_share_vs_flfp():
    med = pd.read_csv(RAW / "medallists_2024.csv")
    flfp = pd.read_csv(RAW / "flfp_ref.csv")
    share = med.groupby("country").gender.apply(lambda s: (s == "Female").mean()).reset_index(
        name="female_medal_share"
    )
    count = med.groupby("country").size().reset_index(name="n_medallists")
    df = share.merge(count).merge(flfp, on="country")
    df = df[df.n_medallists >= 5]
    df.to_csv(CLEAN / "flfp_vs_medal_share.csv", index=False)
    return df


def main():
    r, h = load_results()
    build_sprint_trend(r)
    build_gender_share(r)
    build_host_boost(r, h)
    build_age_by_sport()
    build_medal_type_split()
    build_medals_total_with_econ()
    build_female_medal_share_vs_flfp()
    print("Wrote clean CSVs to", CLEAN)


if __name__ == "__main__":
    main()
