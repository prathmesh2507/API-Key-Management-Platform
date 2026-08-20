
import os
import html
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure, Scatterpolar
import streamlit as st


# ============================================================
# SONORA — Premium Spotify-style Recommendation Studio
# ============================================================
# Recommendation pipeline preserved from the supplied notebook:
# StandardScaler -> NearestNeighbors(metric="cosine", algorithm="brute")
# using the same 14 numerical features.
# ============================================================

st.set_page_config(
    page_title="SONORA • Music Intelligence",
    page_icon="♫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------- Theme -----------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #07070d;
    --panel: rgba(17, 17, 27, .78);
    --panel2: rgba(24, 22, 38, .74);
    --line: rgba(255,255,255,.09);
    --text: #f7f5ff;
    --muted: #9b98ad;
    --violet: #9b5cff;
    --pink: #ff4fa3;
    --cyan: #4de8ff;
    --lime: #c8ff58;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 12% 4%, rgba(155,92,255,.18), transparent 26%),
        radial-gradient(circle at 88% 8%, rgba(255,79,163,.14), transparent 24%),
        radial-gradient(circle at 62% 52%, rgba(77,232,255,.055), transparent 25%),
        #07070d;
    color: var(--text);
}

.stApp:before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
    background-size: 72px 72px;
    mask-image: linear-gradient(to bottom, black, transparent 72%);
    z-index: 0;
}

.block-container {
    max-width: 1420px;
    padding: 1.2rem 3rem 8rem 3rem;
    position: relative;
    z-index: 1;
}

#MainMenu, header, footer {
    visibility: hidden;
}

[data-testid="stSidebar"] {
    display: none;
}

button[kind="secondary"], .stButton > button {
    border: 1px solid rgba(255,255,255,.08) !important;
    background: rgba(255,255,255,.045) !important;
    color: #f7f5ff !important;
    border-radius: 12px !important;
    transition: .25s ease !important;
}

.stButton > button:hover {
    border-color: rgba(155,92,255,.65) !important;
    background: rgba(155,92,255,.12) !important;
    transform: translateY(-1px);
}

[data-testid="stTextInput"] input {
    background: rgba(255,255,255,.055) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    color: white !important;
    border-radius: 15px !important;
    height: 48px !important;
}

[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,.055) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 13px !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(255,255,255,.065), rgba(255,255,255,.025));
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 16px 50px rgba(0,0,0,.18);
}

div[data-testid="stMetricLabel"] {
    color: #9691a8 !important;
}

div[data-testid="stMetricValue"] {
    color: #fff !important;
    font-family: 'Space Grotesk', sans-serif;
}

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 30px;
    min-height: 360px;
    padding: 48px 52px;
    margin: 8px 0 28px 0;
    background:
        radial-gradient(circle at 82% 28%, rgba(255,79,163,.22), transparent 22%),
        radial-gradient(circle at 68% 78%, rgba(77,232,255,.16), transparent 22%),
        linear-gradient(120deg, rgba(30,20,55,.94), rgba(10,11,19,.90));
    box-shadow: 0 30px 100px rgba(0,0,0,.34);
}

.hero:after {
    content: "";
    position: absolute;
    width: 330px;
    height: 330px;
    right: -90px;
    top: -100px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,.08);
    box-shadow:
        0 0 0 34px rgba(155,92,255,.025),
        0 0 0 68px rgba(255,79,163,.025),
        0 0 100px rgba(155,92,255,.18);
    animation: orbit 12s linear infinite;
}

@keyframes orbit {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 1px solid rgba(200,255,88,.25);
    color: #d9ff9a;
    background: rgba(200,255,88,.07);
    border-radius: 999px;
    padding: 7px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(48px, 7vw, 88px);
    line-height: .93;
    letter-spacing: -.055em;
    margin: 24px 0 16px;
    max-width: 780px;
    background: linear-gradient(100deg, #fff 5%, #d7c8ff 42%, #ff7db8 78%, #7df4ff 105%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #aaa5b9;
    font-size: 17px;
    max-width: 670px;
    line-height: 1.65;
}

.hero-orb {
    position: absolute;
    right: 9%;
    bottom: 12%;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: conic-gradient(from 20deg, #9b5cff, #ff4fa3, #4de8ff, #9b5cff);
    filter: blur(.2px);
    box-shadow: 0 0 90px rgba(155,92,255,.4);
    opacity: .84;
    animation: pulse 4s ease-in-out infinite;
}

.hero-orb:before {
    content: "♫";
    position: absolute;
    inset: 10px;
    border-radius: 50%;
    background: #090911;
    display: grid;
    place-items: center;
    font-size: 56px;
    color: white;
}

@keyframes pulse {
    0%,100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -.035em;
    margin: 30px 0 5px;
}

.section-sub {
    color: var(--muted);
    margin-bottom: 18px;
}

.song-card {
    position: relative;
    overflow: hidden;
    min-height: 286px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,.075);
    background:
        linear-gradient(145deg, rgba(255,255,255,.075), rgba(255,255,255,.025)),
        rgba(12,12,19,.75);
    padding: 18px;
    margin-bottom: 14px;
    transition: .3s ease;
}

.song-card:hover {
    transform: translateY(-5px);
    border-color: rgba(155,92,255,.42);
    box-shadow: 0 22px 60px rgba(0,0,0,.32), 0 0 35px rgba(155,92,255,.08);
}

.cover {
    height: 145px;
    border-radius: 17px;
    display: flex;
    align-items: flex-end;
    padding: 14px;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,.7), transparent 4%),
        radial-gradient(circle at 70% 35%, rgba(255,255,255,.24), transparent 22%),
        linear-gradient(135deg, #2b145c, #ff4fa3 52%, #4de8ff);
}

.cover:after {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-radial-gradient(circle at 80% 20%, transparent 0 18px, rgba(255,255,255,.05) 19px 20px);
    opacity: .7;
}

.cover-note {
    position: relative;
    z-index: 2;
    font-size: 46px;
    line-height: 1;
    font-family: 'Space Grotesk', sans-serif;
}

.song-name {
    color: #fff;
    font-size: 17px;
    font-weight: 700;
    margin-top: 13px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.artist-name {
    color: #9d99aa;
    font-size: 13px;
    margin-top: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.tag {
    display: inline-block;
    padding: 4px 8px;
    margin-top: 11px;
    border-radius: 999px;
    background: rgba(155,92,255,.11);
    border: 1px solid rgba(155,92,255,.2);
    color: #cdb7ff;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: .08em;
}

.match {
    position: absolute;
    top: 15px;
    right: 15px;
    padding: 6px 9px;
    border-radius: 999px;
    background: rgba(7,7,13,.7);
    border: 1px solid rgba(200,255,88,.22);
    color: #d9ff9a;
    font-size: 11px;
    font-weight: 700;
    backdrop-filter: blur(10px);
}

.detail-panel {
    border: 1px solid rgba(255,255,255,.08);
    background: linear-gradient(145deg, rgba(30,27,47,.78), rgba(12,12,19,.82));
    border-radius: 25px;
    padding: 26px;
    margin: 18px 0 26px;
}

.detail-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -.04em;
}

.detail-meta {
    color: #a29daf;
    margin-top: 6px;
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
}

.pill {
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(255,255,255,.045);
    color: #c6c1d2;
    padding: 7px 11px;
    border-radius: 999px;
    font-size: 11px;
}

.nav-label {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    letter-spacing: -.02em;
}

.insight {
    border-left: 3px solid #9b5cff;
    background: rgba(155,92,255,.055);
    border-radius: 0 14px 14px 0;
    padding: 14px 16px;
    color: #b9b3c6;
    line-height: 1.6;
}

.empty {
    padding: 70px 20px;
    text-align: center;
    border: 1px dashed rgba(255,255,255,.11);
    border-radius: 24px;
    background: rgba(255,255,255,.02);
}

.empty-big {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    color: white;
}

.small-muted {
    color: #777383;
    font-size: 12px;
}

hr {
    border-color: rgba(255,255,255,.07) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------- Assets -----------------------------

BASE = Path(__file__).resolve().parent

FEATURES_FALLBACK = [
    "popularity",
    "duration_ms",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
]


@st.cache_resource(show_spinner=False)
def load_assets():
    errors = []

    def load_pickle(name):
        path = BASE / name
        if not path.exists():
            errors.append(f"Missing {name}")
            return None
        try:
            return joblib.load(path)
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            return None

    model = load_pickle("spotify_recommender.pkl")
    scaler = load_pickle("scaler.pkl")
    data = load_pickle("spotify_dataset.pkl")
    features = load_pickle("feature_columns.pkl")

    # The notebook's exported pickles are the preferred production path.
    # If they are absent, build the same pipeline from dataset.csv.
    if model is None or scaler is None or data is None or features is None:
        csv_path = BASE / "dataset.csv"
        if not csv_path.exists():
            alt = BASE / "dataset(5).csv"
            if alt.exists():
                csv_path = alt

        if csv_path.exists():
            try:
                from sklearn.neighbors import NearestNeighbors
                from sklearn.preprocessing import StandardScaler

                raw = pd.read_csv(csv_path)

                if "Unnamed: 0" in raw.columns:
                    raw = raw.drop(columns=["Unnamed: 0"])
                if "track_id" in raw.columns:
                    raw = raw.drop(columns=["track_id"])

                raw = raw.drop_duplicates()
                raw = raw.dropna(subset=["artists", "album_name", "track_name"]).copy()

                features = FEATURES_FALLBACK
                X = raw[features]
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)

                model = NearestNeighbors(
                    metric="cosine",
                    algorithm="brute",
                    n_neighbors=6,
                )
                model.fit(X_scaled)
                data = raw

            except Exception as exc:
                errors.append(f"Fallback training failed: {exc}")

    if data is None or scaler is None or model is None:
        return None, None, None, None, errors

    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    if features is None:
        features = FEATURES_FALLBACK

    return model, scaler, data, list(features), errors


model, scaler, df, FEATURES, LOAD_ERRORS = load_assets()

if df is None:
    st.error(
        "The recommendation assets could not be loaded. Put the four notebook-exported "
        "pickle files next to app.py, or place dataset.csv in the same folder."
    )
    if LOAD_ERRORS:
        with st.expander("Technical details"):
            for e in LOAD_ERRORS:
                st.write(e)
    st.stop()

# Defensive cleanup for either exported dataframe or CSV fallback.
for col in ["artists", "album_name", "track_name", "track_genre"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str)

# ----------------------------- Session -----------------------------

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "selected_song" not in st.session_state:
    st.session_state.selected_song = None
if "recent" not in st.session_state:
    st.session_state.recent = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []

def go(page):
    st.session_state.page = page


def select_song(name):
    st.session_state.selected_song = name
    if name and name not in st.session_state.recent:
        st.session_state.recent.insert(0, name)
        st.session_state.recent = st.session_state.recent[:8]


# ----------------------------- Recommendation engine -----------------------------

def find_song_exact_or_best(query):
    query = str(query).strip()
    if not query:
        return None, None

    names = df["track_name"].astype(str)
    exact = df[names.str.lower() == query.lower()]
    if not exact.empty:
        idx_label = exact.index[0]
        return exact.iloc[0], df.index.get_loc(idx_label)

    mask = names.str.contains(query, case=False, na=False)
    matches = df.loc[mask]
    if not matches.empty:
        row = matches.iloc[0]
        return row, df.index.get_loc(matches.index[0])

    return None, None


def recommend_songs(song_name, n_recommendations=6):
    """
    Same recommendation method as the supplied notebook:
    - exact track-name lookup first
    - use the scaled feature vector
    - NearestNeighbors cosine distance
    - skip the source song
    - return song / artist / album / genre / popularity
    """
    song, row_position = find_song_exact_or_best(song_name)

    if song is None:
        return pd.DataFrame(), None

    n = min(int(n_recommendations), max(1, len(df) - 1))
    distances, indices = model.kneighbors(
        [scaler.transform(df.iloc[[row_position]][FEATURES])[0]],
        n_neighbors=n + 1,
    )

    # If the exported model was trained on the exact notebook data,
    # its neighbor indices directly map to the dataframe row order.
    rec_rows = []
    for dist, i in zip(distances[0][1:], indices[0][1:]):
        if i >= len(df):
            continue
        row = df.iloc[int(i)]
        rec_rows.append(
            {
                "Song": row.get("track_name", ""),
                "Artist": row.get("artists", ""),
                "Album": row.get("album_name", ""),
                "Genre": row.get("track_genre", ""),
                "Popularity": row.get("popularity", 0),
                "Distance": float(dist),
                "Similarity": float(max(0.0, 1.0 - dist)),
            }
        )

    return pd.DataFrame(rec_rows), song


def catalog_search(query, limit=8):
    if not query:
        return df.head(0)

    q = str(query).strip().lower()
    name = df["track_name"].str.lower()
    artist = df["artists"].str.lower()
    album = df["album_name"].str.lower()

    mask = (
        name.str.contains(q, na=False)
        | artist.str.contains(q, na=False)
        | album.str.contains(q, na=False)
    )

    results = df.loc[mask].copy()
    if results.empty:
        return results

    # Prefer exact title, then title prefix, then popularity.
    results["_exact"] = (name.loc[results.index] == q).astype(int)
    results["_prefix"] = name.loc[results.index].str.startswith(q).astype(int)
    results = results.sort_values(
        ["_exact", "_prefix", "popularity"],
        ascending=[False, False, False],
    )
    return results.head(limit)


def cover_gradient(i):
    palettes = [
        ("#6d28d9", "#ec4899", "#22d3ee"),
        ("#db2777", "#7c3aed", "#38bdf8"),
        ("#0f766e", "#06b6d4", "#8b5cf6"),
        ("#ea580c", "#e11d48", "#7c3aed"),
        ("#2563eb", "#7c3aed", "#ec4899"),
        ("#16a34a", "#0891b2", "#8b5cf6"),
    ]
    a, b, c = palettes[i % len(palettes)]
    return f"linear-gradient(135deg, {a}, {b} 55%, {c})"


def genre_label(value):
    text = str(value or "").replace("-", " ").replace("_", " ")
    return text.title()[:22]


def mood_for(row):
    energy = float(row.get("energy", 0) or 0)
    valence = float(row.get("valence", 0) or 0)
    dance = float(row.get("danceability", 0) or 0)

    if energy > .72 and dance > .68:
        return "HIGH ENERGY"
    if valence > .70:
        return "FEEL GOOD"
    if energy < .35 and float(row.get("acousticness", 0) or 0) > .65:
        return "CHILL"
    if float(row.get("instrumentalness", 0) or 0) > .55:
        return "INSTRUMENTAL"
    return "VIBE MATCH"


def render_song_cards(data, title=None, show_match=True):
    if data is None or len(data) == 0:
        st.markdown(
            '<div class="empty"><div class="empty-big">No tracks found</div>'
            '<div class="small-muted">Try a different title, artist, or album.</div></div>',
            unsafe_allow_html=True,
        )
        return

    if title:
        st.markdown(f'<div class="section-title">{html.escape(title)}</div>', unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    for pos, (_, row) in enumerate(data.iterrows()):
        with cols[pos % 3]:
            song = str(row.get("Song", row.get("track_name", "")))
            artist = str(row.get("Artist", row.get("artists", "")))
            album = str(row.get("Album", row.get("album_name", "")))
            genre = str(row.get("Genre", row.get("track_genre", "")))
            popularity = float(row.get("Popularity", row.get("popularity", 0)) or 0)
            similarity = row.get("Similarity", None)

            if similarity is not None and pd.notna(similarity):
                match = int(np.clip(round(float(similarity) * 100), 1, 99))
            else:
                match = int(np.clip(round(popularity), 0, 100))

            grad = cover_gradient(pos)
            mood = mood_for(row)

            st.markdown(
                f"""
                <div class="song-card">
                    <div class="match">{match}% MATCH</div>
                    <div class="cover" style="background:{grad}">
                        <div class="cover-note">♫</div>
                    </div>
                    <div class="song-name">{html.escape(song)}</div>
                    <div class="artist-name">{html.escape(artist)}</div>
                    <span class="tag">{html.escape(mood)}</span>
                    <span class="tag">{html.escape(genre_label(genre))}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Save control lives outside the HTML card so Streamlit buttons work.
            is_fav = song in st.session_state.favorites
            if st.button(
                "♥  Saved" if is_fav else "♡  Save",
                key=f"save_{st.session_state.page}_{pos}_{song}",
                use_container_width=True,
            ):
                if is_fav:
                    st.session_state.favorites.remove(song)
                else:
                    st.session_state.favorites.append(song)
                st.rerun()


# ----------------------------- Navigation -----------------------------

nav1, nav2, nav3, nav4, nav5 = st.columns([1.1, 1, 1, 1, 1.2])

with nav1:
    st.markdown(
        '<div class="nav-label" style="font-size:22px;">SONORA<span style="color:#ff4fa3">.</span></div>',
        unsafe_allow_html=True,
    )

for col, label, page in [
    (nav2, "⌂  Home", "Home"),
    (nav3, "⌕  Discover", "Discover"),
    (nav4, "◈  Analytics", "Analytics"),
    (nav5, "♡  Library", "Library"),
]:
    with col:
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            go(page)
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ----------------------------- HOME -----------------------------

if st.session_state.page == "Home":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">✦ AI MUSIC INTELLIGENCE</div>
            <h1>Your sound.<br>Better matched.</h1>
            <p>
                Discover tracks through audio similarity — not just popularity.
                SONORA reads the musical DNA of each track and surfaces the songs
                that belong in the same listening universe.
            </p>
            <div class="hero-orb"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("TRACKS", f"{len(df):,}")
    with c2:
        st.metric("ARTISTS", f"{df['artists'].nunique():,}")
    with c3:
        st.metric("GENRES", f"{df['track_genre'].nunique():,}")
    with c4:
        st.metric("AUDIO FEATURES", f"{len(FEATURES)}")

    st.markdown('<div class="section-title">Find your next obsession</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Search by song, artist or album. Then let the model do the digging.</div>',
        unsafe_allow_html=True,
    )

    search_col, button_col = st.columns([5, 1])
    with search_col:
        q = st.text_input(
            "Search",
            placeholder="Try “Shape of You”, “Believer”, “Jason Mraz”…",
            label_visibility="collapsed",
            key="home_search",
        )
    with button_col:
        run = st.button("✦ Discover", use_container_width=True)

    if run and q.strip():
        select_song(q.strip())
        st.session_state.page = "Discover"
        st.rerun()

    st.markdown('<div class="section-title">Curated for the curious</div>', unsafe_allow_html=True)

    top = (
        df.sort_values("popularity", ascending=False)
        .drop_duplicates(subset=["track_name", "artists"])
        .head(6)
        .copy()
    )
    render_song_cards(top)

    if st.session_state.recent:
        st.markdown('<div class="section-title">Recently explored</div>', unsafe_allow_html=True)
        recent_rows = []
        for name in st.session_state.recent:
            row, _ = find_song_exact_or_best(name)
            if row is not None:
                recent_rows.append(row)
        if recent_rows:
            render_song_cards(pd.DataFrame(recent_rows).head(6))

# ----------------------------- DISCOVER -----------------------------

elif st.session_state.page == "Discover":
    st.markdown(
        '<div class="section-title" style="font-size:40px;">Discover your sound</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-sub">One track in. Six nearby musical universes out.</div>',
        unsafe_allow_html=True,
    )

    q = st.text_input(
        "Song search",
        value=st.session_state.selected_song or "",
        placeholder="Search a track title, artist or album…",
        label_visibility="collapsed",
        key="discover_search",
    )

    suggestions = catalog_search(q, 7)
    if q.strip() and not suggestions.empty:
        st.markdown('<div class="small-muted">Matching catalog entries</div>', unsafe_allow_html=True)
        for i, (_, r) in enumerate(suggestions.iterrows()):
            a, b = st.columns([5, 1])
            with a:
                st.markdown(
                    f"**{html.escape(str(r['track_name']))}**  ·  "
                    f"<span style='color:#8e899a'>{html.escape(str(r['artists']))}</span>",
                    unsafe_allow_html=True,
                )
            with b:
                if st.button("Use", key=f"use_{i}_{r['track_name']}"):
                    select_song(str(r["track_name"]))
                    st.rerun()

    if q.strip():
        recs, source = recommend_songs(q, 6)

        if source is not None:
            select_song(str(source["track_name"]))

            st.markdown(
                f"""
                <div class="detail-panel">
                    <div class="small-muted">NOW ANALYZING</div>
                    <div class="detail-title">{html.escape(str(source["track_name"]))}</div>
                    <div class="detail-meta">
                        {html.escape(str(source["artists"]))}
                        &nbsp; • &nbsp;
                        {html.escape(str(source["album_name"]))}
                    </div>
                    <div class="pill-row">
                        <span class="pill">Genre · {html.escape(genre_label(source["track_genre"]))}</span>
                        <span class="pill">Popularity · {int(source["popularity"])}/100</span>
                        <span class="pill">Energy · {float(source["energy"]):.2f}</span>
                        <span class="pill">Danceability · {float(source["danceability"]):.2f}</span>
                        <span class="pill">Valence · {float(source["valence"]):.2f}</span>
                        <span class="pill">Tempo · {float(source["tempo"]):.1f} BPM</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="insight">✦ Recommendations are generated from the same '
                '14-feature standardized audio representation and cosine-nearest-neighbor '
                'model used in the supplied notebook.</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="section-title">Your next 6</div><div class="section-sub">'
                'Similarity-first. No playlist filler.</div>',
                unsafe_allow_html=True,
            )
            render_song_cards(recs, show_match=True)
        else:
            st.markdown(
                '<div class="empty"><div class="empty-big">Nothing in the catalog yet.</div>'
                '<div class="small-muted">Try a different spelling or search by artist.</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="empty"><div class="empty-big">Start with a song.</div>'
            '<div class="small-muted">The recommendation engine will map its audio fingerprint to nearby tracks.</div></div>',
            unsafe_allow_html=True,
        )

# ----------------------------- ANALYTICS -----------------------------

elif st.session_state.page == "Analytics":
    st.markdown(
        '<div class="section-title" style="font-size:40px;">Music intelligence</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-sub">A visual fingerprint of the catalog powering your recommendations.</div>',
        unsafe_allow_html=True,
    )

    a, b, c, d = st.columns(4)
    with a:
        st.metric("AVG ENERGY", f"{df['energy'].mean():.2f}")
    with b:
        st.metric("AVG DANCEABILITY", f"{df['danceability'].mean():.2f}")
    with c:
        st.metric("AVG VALENCE", f"{df['valence'].mean():.2f}")
    with d:
        st.metric("AVG TEMPO", f"{df['tempo'].mean():.0f} BPM")

    chart_df = df.copy()

    left, right = st.columns(2)

    with left:
        genre_counts = (
            chart_df["track_genre"]
            .value_counts()
            .head(15)
            .sort_values()
            .reset_index()
        )
        genre_counts.columns = ["genre", "tracks"]

        fig = px.bar(
            genre_counts,
            x="tracks",
            y="genre",
            orientation="h",
            title="Top genres by catalog size",
        )
        fig.update_layout(
            template="plotly_dark",
            height=520,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dcd7e8",
            title_font_size=18,
            margin=dict(l=0, r=10, t=55, b=10),
        )
        fig.update_traces(
            marker=dict(
                color="rgba(155,92,255,.82)",
                line=dict(color="rgba(255,255,255,.08)", width=1),
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        scatter = chart_df.sample(min(6000, len(chart_df)), random_state=42)
        fig2 = px.scatter(
            scatter,
            x="danceability",
            y="energy",
            size="popularity",
            color="valence",
            hover_name="track_name",
            hover_data=["artists", "track_genre"],
            color_continuous_scale=["#4de8ff", "#9b5cff", "#ff4fa3"],
            title="The catalog's energy × danceability field",
        )
        fig2.update_layout(
            template="plotly_dark",
            height=520,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dcd7e8",
            title_font_size=18,
            margin=dict(l=0, r=0, t=55, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Audio DNA</div>', unsafe_allow_html=True)

    audio_features = [
        "danceability",
        "energy",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
    ]

    means = chart_df[audio_features].mean().values
    labels = [x.replace("_", " ").title() for x in audio_features]

    radar = Figure(
        data=[
            Scatterpolar(
                r=means,
                theta=labels,
                fill="toself",
                line=dict(color="#ff4fa3", width=3),
                fillcolor="rgba(155,92,255,.20)",
            )
        ]
    )
    radar.update_layout(
        template="plotly_dark",
        height=500,
        polar=dict(
            bgcolor="rgba(255,255,255,.025)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="rgba(255,255,255,.08)",
            ),
            angularaxis=dict(gridcolor="rgba(255,255,255,.08)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#dcd7e8",
        margin=dict(l=30, r=30, t=25, b=25),
        showlegend=False,
    )
    st.plotly_chart(radar, use_container_width=True)

    st.markdown(
        '<div class="insight">The recommendation engine uses popularity, duration, '
        'danceability, energy, key, loudness, mode, speechiness, acousticness, '
        'instrumentalness, liveness, valence, tempo and time signature — standardized '
        'before cosine-nearest-neighbor search.</div>',
        unsafe_allow_html=True,
    )

# ----------------------------- LIBRARY -----------------------------

elif st.session_state.page == "Library":
    st.markdown(
        '<div class="section-title" style="font-size:40px;">Your library</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-sub">Tracks you saved or explored during this session.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.favorites:
        fav_rows = []
        for name in st.session_state.favorites:
            row, _ = find_song_exact_or_best(name)
            if row is not None:
                fav_rows.append(row)

        st.markdown('<div class="section-title">Saved tracks</div>', unsafe_allow_html=True)
        render_song_cards(pd.DataFrame(fav_rows))
    else:
        st.markdown(
            '<div class="empty"><div class="empty-big">Your library is empty.</div>'
            '<div class="small-muted">Hit “Save” on a recommendation to build your collection.</div></div>',
            unsafe_allow_html=True,
        )

    if st.session_state.recent:
        st.markdown('<div class="section-title">Recently explored</div>', unsafe_allow_html=True)
        recent_rows = []
        for name in st.session_state.recent:
            row, _ = find_song_exact_or_best(name)
            if row is not None:
                recent_rows.append(row)
        if recent_rows:
            render_song_cards(pd.DataFrame(recent_rows).head(6))



# Tiny status line — deliberately subtle.
st.markdown(
    """
    <div style="text-align:center;color:#5f5b6b;font-size:10px;margin-top:40px;letter-spacing:.08em;">
        SONORA · MUSIC RECOMMENDATION STUDIO · COSINE SIMILARITY ENGINE
    </div>
    """,
    unsafe_allow_html=True,
)
