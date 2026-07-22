"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    user_prefs1 = {"genre": "rock", "mood": "sad", "energy": 0.7}
    user_prefs2 = {"genre": "rap", "mood": "sad", "energy": 0.4}
    user_prefs3 = {"genre": "hip-hop", "mood": "sad", "energy": 0.6}


    print("\nUser profile:")
    for key, value in user_prefs3.items():
        print(f"  {key}: {value}")

    recommendations = recommend_songs(user_prefs3, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
