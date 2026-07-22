import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# Relative importance of each feature. Genre dominates, then mood, energy,
# and acousticness contribute equally. Only the features a user actually
# expresses a preference for are counted (see _score_features).
WEIGHTS = {"genre": 0.2, "mood": 0.2, "energy": 0.4, "acoustic": 0.2}


def _closeness(target: float, value: float) -> float:
    """
    Reward proximity, not magnitude: 1.0 when value == target, falling toward
    0.0 as they diverge. Clamped to [0, 1] so an out-of-range target (e.g. an
    energy of 6 on a 0-1 scale) can't poison the score with negative values.
    """
    return max(0.0, 1.0 - abs(target - value))


def _score_features(
    genre_pref: Optional[str],
    mood_pref: Optional[str],
    energy_pref: Optional[float],
    acoustic_pref: Optional[bool],
    song_genre: str,
    song_mood: str,
    song_energy: float,
    song_acousticness: float,
) -> Tuple[float, List[str]]:
    """
    Core scoring rule shared by the OOP and functional APIs.

    Each feature contributes a *closeness-to-preference* score, weighted by
    WEIGHTS. A feature is only scored when the user expresses a preference for
    it (a non-None arg); the final score is normalized by the total active
    weight so it always lands in [0, 1] regardless of which prefs were given.

    Returns (score, reasons) where reasons is a list of human-readable strings.
    """
    score = 0.0
    active_weight = 0.0
    reasons: List[str] = []

    if genre_pref is not None:
        active_weight += WEIGHTS["genre"]
        if song_genre == genre_pref:
            score += WEIGHTS["genre"]
            reasons.append(f"matches your favorite genre ({genre_pref})")

    # TEMP: mood check disabled to see how rankings shift without it.
    # if mood_pref is not None:
    #     active_weight += WEIGHTS["mood"]
    #     if song_mood == mood_pref:
    #         score += WEIGHTS["mood"]
    #         reasons.append(f"matches your mood ({mood_pref})")

    if energy_pref is not None:
        active_weight += WEIGHTS["energy"]
        closeness = _closeness(energy_pref, song_energy)
        score += WEIGHTS["energy"] * closeness
        if closeness >= 0.8:
            reasons.append(
                f"energy is close to your target ({song_energy:.2f} vs {energy_pref:.2f})"
            )

    if acoustic_pref is not None:
        active_weight += WEIGHTS["acoustic"]
        target = 1.0 if acoustic_pref else 0.0
        closeness = _closeness(target, song_acousticness)
        score += WEIGHTS["acoustic"] * closeness
        if closeness >= 0.7:
            label = "acoustic" if acoustic_pref else "produced/electronic"
            reasons.append(f"has the {label} sound you prefer")

    # Normalize so a partial profile (e.g. no acoustic pref) still scores in [0, 1].
    if active_weight > 0:
        score /= active_weight

    if not reasons:
        reasons.append("a general match for your preferences")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a Song against a UserProfile, returning (score, reasons)."""
        return _score_features(
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            user.likes_acoustic,
            song.genre,
            song.mood,
            song.energy,
            song.acousticness,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # Score every song, then rank highest-first and keep the top k.
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = self._score(user, song)
        return "Recommended because it " + ", ".join(reasons) + "."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file, converting numeric columns to numbers.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs is a dict that may contain any of: "genre", "mood", "energy",
    "likes_acoustic". Missing keys are simply not scored.
    """
    return _score_features(
        user_prefs.get("genre"),
        user_prefs.get("mood"),
        user_prefs.get("energy"),
        user_prefs.get("likes_acoustic"),
        song["genre"],
        song["mood"],
        float(song["energy"]),
        float(song["acousticness"]),
    )


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns (song_dict, score, explanation) tuples, highest score first.
    """
    # 1. Score every song (list comprehension unpacks (score, reasons)).
    scored = [
        (song, *score_song(user_prefs, song))  # (song, score, reasons)
        for song in songs
    ]
    # 2. Rank highest-first (in-place sort of our own local list).
    scored.sort(key=lambda item: item[1], reverse=True)
    # 3. Keep the top k and turn each reasons list into an explanation string.
    return [(song, score, ", ".join(reasons)) for song, score, reasons in scored[:k]]
