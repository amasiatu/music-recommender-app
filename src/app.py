"""
Browser UI for the Music Recommender Simulation.

Runs both paths in the browser via Streamlit:
  - RAG assistant  : type a plain-English request, get a grounded recommendation
  - Scoring picker : set a taste profile, get ranked recommendations with reasons

Run it from the project root:
    streamlit run src/app.py

The RAG tab's retrieval works with no API key. To enable Claude's written
recommendation, set ANTHROPIC_API_KEY in your environment before launching.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

# Streamlit runs this file directly, so its folder (src/) is on sys.path and
# these plain imports resolve.
from recommender import load_songs, recommend_songs
from rag import retrieve_songs, format_context, rag_recommend

# Resolve the catalog relative to this file so it works from any directory.
SONGS_CSV = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


@st.cache_data
def get_songs():
    """Load the catalog once and cache it across reruns."""
    return load_songs(str(SONGS_CSV))


def main() -> None:
    st.set_page_config(page_title="Music Recommender", page_icon="🎵")
    st.title("🎵 Music Recommender Simulation")

    songs = get_songs()
    st.caption(f"Loaded {len(songs)} songs from the catalog.")

    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if not has_key:
        st.info(
            "No ANTHROPIC_API_KEY set — the RAG tab will show the songs it "
            "retrieved instead of an AI-written recommendation.",
            icon="ℹ️",
        )

    rag_tab, score_tab = st.tabs(["RAG assistant", "Scoring recommender"])

    # ---------- RAG assistant ----------
    with rag_tab:
        st.subheader("Ask in plain English")
        query = st.text_input(
            "What do you want to listen to?",
            value="chill music for late-night studying",
        )
        k = st.slider("How many songs to retrieve", 1, 10, 5)

        if st.button("Recommend", key="rag_go"):
            with st.spinner("Retrieving from the catalog…"):
                answer = rag_recommend(query, songs, k=k)
            st.markdown(answer)

            with st.expander("See the retrieved songs (the RAG context)"):
                retrieved = retrieve_songs(query, songs, k=k)
                if retrieved:
                    st.code(format_context(retrieved), language="text")
                else:
                    st.write("No songs matched — try a genre, mood, or vibe.")

    # ---------- Scoring recommender ----------
    with score_tab:
        st.subheader("Set a taste profile")
        genres = sorted({s["genre"] for s in songs})
        moods = sorted({s["mood"] for s in songs})

        col1, col2 = st.columns(2)
        with col1:
            genre = st.selectbox("Favorite genre", genres)
        with col2:
            mood = st.selectbox("Favorite mood", moods)
        energy = st.slider("Target energy", 0.0, 1.0, 0.8, 0.05)
        top_k = st.slider("How many recommendations", 1, 10, 5, key="score_k")

        if st.button("Recommend", key="score_go"):
            prefs = {"genre": genre, "mood": mood, "energy": energy}
            results = recommend_songs(prefs, songs, k=top_k)
            for song, score, reasons in results:
                st.markdown(f"**{song['title']}** — {song['artist']}  ·  score {score:.2f}")
                st.caption(f"Because: {reasons}")


if __name__ == "__main__":
    main()
