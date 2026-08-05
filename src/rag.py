"""
RAG music assistant: ask for music in plain English, get a grounded answer.

This is a small Retrieval-Augmented Generation (RAG) pipeline built on top of
the song catalog in data/songs.csv:

  1. RETRIEVE  - rank the songs in the CSV against a free-text query
                 (e.g. "something upbeat for a workout") and keep the top matches.
  2. AUGMENT   - format those retrieved songs into a context block.
  3. GENERATE  - hand that context to Claude and ask it to write a recommendation
                 grounded ONLY in the retrieved songs (no inventing tracks).

The catalog is the "source" the model retrieves from. Grounding the model in the
retrieved rows is the whole point of RAG: it can only recommend songs that
actually exist in the data, which keeps it honest.

Run it:
    python -m src.rag "chill music for late-night studying"

Requires an Anthropic API key in the environment:
    export ANTHROPIC_API_KEY=sk-ant-...
Without a key, the retrieval step still runs and prints the matched songs.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Dict, List, Tuple

# Support both `python -m src.rag` (package-relative) and a direct run.
try:
    from .recommender import load_songs
except ImportError:  # pragma: no cover - fallback for direct execution
    from recommender import load_songs


MODEL = "claude-opus-4-8"

# Words in a query that hint at how energetic the listener wants the music to be.
# Retrieval uses these to nudge songs toward the right energy range, since a
# request like "for the gym" never literally says "energy 0.9".
_HIGH_ENERGY_HINTS = {
    "workout", "gym", "run", "running", "cardio", "energetic", "energy",
    "hype", "pump", "party", "dance", "dancing", "intense", "upbeat",
    "fast", "hard", "aggressive", "loud",
}
_LOW_ENERGY_HINTS = {
    "chill", "relax", "relaxing", "study", "studying", "focus", "focused",
    "sleep", "sleepy", "calm", "mellow", "quiet", "slow", "soft", "soothing",
    "ambient", "background", "reading", "unwind",
}

# Fields we match query words against, ordered by how much a hit should count.
_FIELD_WEIGHTS = {
    "genre": 3.0,
    "mood": 3.0,
    "artist": 1.5,
    "title": 1.0,
}

# Common filler words stripped from the query before keyword matching, so a
# stopword like "the" can't spuriously match an artist name (e.g. "the Tides").
_STOPWORDS = {
    "a", "an", "and", "the", "for", "of", "to", "in", "on", "at", "with",
    "some", "something", "music", "songs", "song", "track", "tracks", "me",
    "i", "want", "need", "give", "play", "please", "that", "is", "are", "my",
    "like", "would", "can", "you", "get", "find", "looking", "listen",
}


def _tokenize(text: str) -> List[str]:
    """Lowercase word tokens, e.g. 'Hip-Hop beats!' -> ['hip', 'hop', 'beats']."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _relevance(query: str, song: Dict) -> float:
    """
    Score how well a single song matches a free-text query.

    Two signals combine:
      - keyword overlap between the query and the song's genre/mood/artist/title
      - energy alignment inferred from hint words in the query

    Returns a non-negative float; higher means more relevant.
    """
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return 0.0

    score = 0.0

    # 1. Keyword overlap against each catalog field.
    for field, weight in _FIELD_WEIGHTS.items():
        field_tokens = set(_tokenize(str(song.get(field, ""))))
        score += weight * len(q_tokens & field_tokens)

    # 2. Energy alignment. If the query leans energetic, reward high-energy
    #    songs (and vice versa) so "gym music" surfaces the loud tracks even
    #    when no genre word matches.
    energy = float(song.get("energy", 0.0))
    if q_tokens & _HIGH_ENERGY_HINTS:
        score += 2.0 * energy
    if q_tokens & _LOW_ENERGY_HINTS:
        score += 2.0 * (1.0 - energy)

    return score


def retrieve_songs(query: str, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float]]:
    """
    RETRIEVAL step: rank the catalog against the query and return the top k
    (song, score) pairs, highest first. Songs with zero relevance are dropped,
    so a nonsense query returns nothing rather than random tracks.
    """
    scored = [(song, _relevance(query, song)) for song in songs]
    scored = [pair for pair in scored if pair[1] > 0]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


def format_context(retrieved: List[Tuple[Dict, float]]) -> str:
    """
    AUGMENT step: turn retrieved songs into a plain-text block the model can read.
    Only these songs are shown to the model, so it can only recommend from them.
    """
    lines = []
    for song, _score in retrieved:
        lines.append(
            f"- \"{song['title']}\" by {song['artist']} "
            f"(genre: {song['genre']}, mood: {song['mood']}, "
            f"energy: {song['energy']:.2f}, tempo: {int(song['tempo_bpm'])} bpm, "
            f"danceability: {song['danceability']:.2f}, "
            f"acousticness: {song['acousticness']:.2f})"
        )
    return "\n".join(lines)


SYSTEM_PROMPT = (
    "You are a friendly music recommender for a small demo app. "
    "You will be given a listener's request and a numbered list of candidate "
    "songs retrieved from the app's catalog. Recommend songs ONLY from that "
    "list - never invent songs, artists, or details that are not shown. "
    "Pick the 2-3 best matches, and for each one give a short, specific reason "
    "tied to the song's attributes (genre, mood, energy, tempo, etc.). "
    "If none of the candidates fit the request, say so honestly. "
    "Keep the whole reply under 150 words and address the listener directly."
)


def generate_recommendation(query: str, context: str) -> str:
    """
    GENERATION step: ask Claude to recommend from the retrieved songs only.

    Returns the model's text. Raises RuntimeError with a clear message if the
    anthropic package or an API key is unavailable, so the caller can fall back
    to showing the retrieved songs on their own.
    """
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - depends on install
        raise RuntimeError(
            "The 'anthropic' package is not installed. Run: pip install -r requirements.txt"
        ) from exc

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export your key to enable AI recommendations:\n"
            "    export ANTHROPIC_API_KEY=sk-ant-..."
        )

    client = anthropic.Anthropic()

    user_message = (
        f"Listener's request: {query}\n\n"
        f"Candidate songs retrieved from the catalog:\n{context}\n\n"
        "Recommend the best matches from this list."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    # response.content is a list of blocks; collect the text ones.
    return "".join(block.text for block in response.content if block.type == "text").strip()


def rag_recommend(query: str, songs: List[Dict], k: int = 5) -> str:
    """
    Full RAG pipeline: retrieve -> augment -> generate. Returns a printable string.

    If retrieval finds nothing, or the model can't be reached, this still returns
    something useful instead of crashing.
    """
    retrieved = retrieve_songs(query, songs, k=k)

    if not retrieved:
        return (
            "I couldn't find any songs in the catalog that match that request. "
            "Try describing a genre, mood, or vibe (e.g. \"upbeat pop for a run\")."
        )

    context = format_context(retrieved)

    try:
        answer = generate_recommendation(query, context)
        return f"{answer}\n\n(Retrieved from {len(retrieved)} candidate songs in the catalog.)"
    except RuntimeError as exc:
        # No AI available - fall back to just showing what retrieval found.
        return (
            f"AI recommendation unavailable: {exc}\n\n"
            f"Here are the {len(retrieved)} closest songs I retrieved from the catalog:\n"
            f"{context}"
        )


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        query = "something upbeat and energetic for a workout"
        print(f"(no query given - using default: \"{query}\")\n")

    songs = load_songs("data/songs.csv")

    print(f"Your request: {query}\n")
    print(rag_recommend(query, songs, k=5))


if __name__ == "__main__":
    main()
