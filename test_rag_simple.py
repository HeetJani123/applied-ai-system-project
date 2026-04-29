#!/usr/bin/env python
"""Quick test of RAG search functionality."""

from src.recommender import load_songs, search_songs_by_query, search_songs_by_genre, search_songs_by_mood
from pathlib import Path

# Load songs
data_path = Path(__file__).parent / "data" / "songs.csv"
songs = load_songs(str(data_path))

# Create lookup dict
song_dict = {s.id: s for s in songs}

print("=" * 60)
print("RAG SEMANTIC SEARCH TEST")
print("=" * 60)

# Test semantic search
print("\n📌 Semantic Query: 'upbeat pop music'")
results = search_songs_by_query(songs, "upbeat pop music", top_k=5)
for song_id, score in results:
    song = song_dict[song_id]
    print(f"  {song.title:<25} (score: {score:.3f}) - {song.genre}, {song.mood}")

# Test genre search
print("\n📌 Genre Search: 'pop'")
results = search_songs_by_genre(songs, "pop", top_k=3)
for song_id in results:
    song = song_dict[song_id]
    print(f"  {song.title:<25} - {song.artist}")

# Test mood search
print("\n📌 Mood Search: 'chill'")
results = search_songs_by_mood(songs, "chill", top_k=3)
for song_id in results:
    song = song_dict[song_id]
    print(f"  {song.title:<25} - {song.genre}")

print("\n✅ RAG functionality working!\n")
