"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(label: str, user_prefs: dict, songs: list) -> None:
    print(f"\n=== {label} ===\n")
    recommendations = recommend_songs(user_prefs, songs, k=5)

    for index, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        print(f"{index}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Reasons: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv") 

    profiles = [
        ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.85}),
        ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.35}),
        ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.9}),
        ("Conflicting Energy-Sad", {"genre": "pop", "mood": "sad", "energy": 0.9}),
    ]

    for label, user_prefs in profiles:
        print_recommendations(label, user_prefs, songs)


if __name__ == "__main__":
    main()
