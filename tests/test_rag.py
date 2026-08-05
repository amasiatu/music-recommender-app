"""
Reliability tests for the RAG assistant's retrieval + grounding logic.

These run without an API key: they exercise the RETRIEVE and AUGMENT stages
(the parts my code controls), which is where a RAG system's correctness is
decided. The GENERATE stage calls Claude and is covered by the no-key fallback
test below plus human review (see model_card.md).
"""

from src.rag import retrieve_songs, format_context, rag_recommend, _relevance

# A tiny fixed catalog so expectations are deterministic and easy to reason about.
SONGS = [
    {"id": 1, "title": "Gym Anthem", "artist": "Max Pulse", "genre": "pop",
     "mood": "intense", "energy": 0.95, "tempo_bpm": 130, "valence": 0.7,
     "danceability": 0.9, "acousticness": 0.05},
    {"id": 2, "title": "Quiet Library", "artist": "Paper Lanterns", "genre": "lofi",
     "mood": "chill", "energy": 0.30, "tempo_bpm": 72, "valence": 0.5,
     "danceability": 0.5, "acousticness": 0.90},
    {"id": 3, "title": "Rock Storm", "artist": "Voltline", "genre": "rock",
     "mood": "aggressive", "energy": 0.90, "tempo_bpm": 150, "valence": 0.4,
     "danceability": 0.6, "acousticness": 0.10},
    {"id": 4, "title": "Soft Piano", "artist": "Aria Vale", "genre": "classical",
     "mood": "calm", "energy": 0.20, "tempo_bpm": 60, "valence": 0.3,
     "danceability": 0.2, "acousticness": 0.95},
]


def test_retrieve_ranks_by_relevance_and_respects_k():
    """Top-k are returned, sorted highest-score first, never more than k."""
    results = retrieve_songs("rock", SONGS, k=2)
    assert len(results) <= 2
    scores = [score for _song, score in results]
    assert scores == sorted(scores, reverse=True)  # descending
    # An exact genre match ("rock") should be the top hit.
    assert results[0][0]["genre"] == "rock"


def test_retrieve_uses_energy_hints_for_low_energy_requests():
    """A 'chill studying' request should surface low-energy songs, not the gym track."""
    results = retrieve_songs("chill music for studying", SONGS, k=2)
    top_titles = [song["title"] for song, _score in results]
    assert "Gym Anthem" not in top_titles
    assert any(song["energy"] < 0.4 for song, _score in results)


def test_retrieve_drops_zero_relevance_matches():
    """A nonsense query returns nothing rather than random songs."""
    assert retrieve_songs("zzzzzz qwerty", SONGS, k=5) == []


def test_relevance_is_non_negative():
    """Scores are always >= 0 so ranking is well-defined."""
    for song in SONGS:
        assert _relevance("happy pop", song) >= 0.0


def test_context_is_grounded_only_in_retrieved_songs():
    """AUGMENT step: the context block must contain exactly the retrieved songs."""
    retrieved = retrieve_songs("rock", SONGS, k=2)
    context = format_context(retrieved)
    for song, _score in retrieved:
        assert song["title"] in context
    # A song that was NOT retrieved must not leak into the context.
    assert "Soft Piano" not in context


def test_no_match_returns_helpful_message():
    """rag_recommend degrades gracefully (no crash) when nothing matches."""
    answer = rag_recommend("zzzzzz qwerty", SONGS, k=5)
    assert isinstance(answer, str)
    assert "couldn't find" in answer.lower()
