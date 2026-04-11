from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import csv


NUMERIC_FIELDS = {"id", "energy", "tempo_bpm", "valence", "danceability", "acousticness"}


def score_song(user_prefs: Dict[str, Any], song: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score one song against a user profile."""
    score = 0.0
    reasons: List[str] = []

    if user_prefs.get("genre") and song.get("genre") == user_prefs.get("genre"):
        score += 1.0
        reasons.append("genre match (+1.0)")

    if user_prefs.get("mood") and song.get("mood") == user_prefs.get("mood"):
        score += 1.0
        reasons.append("mood match (+1.0)")

    target_energy = user_prefs.get("energy")
    song_energy = song.get("energy")
    if target_energy is not None and song_energy is not None:
        energy_similarity = max(0.0, 1.0 - abs(float(song_energy) - float(target_energy)))
        energy_points = 4.0 * energy_similarity
        score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.2f})")

    target_tempo = user_prefs.get("tempo_bpm")
    song_tempo = song.get("tempo_bpm")
    if target_tempo is not None and song_tempo is not None:
        tempo_similarity = max(0.0, 1.0 - abs(float(song_tempo) - float(target_tempo)) / 120.0)
        tempo_points = 0.5 * tempo_similarity
        if tempo_points > 0:
            score += tempo_points
            reasons.append(f"tempo closeness (+{tempo_points:.2f})")

    target_danceability = user_prefs.get("danceability")
    song_danceability = song.get("danceability")
    if target_danceability is not None and song_danceability is not None:
        dance_similarity = max(0.0, 1.0 - abs(float(song_danceability) - float(target_danceability)))
        dance_points = 0.5 * dance_similarity
        if dance_points > 0:
            score += dance_points
            reasons.append(f"danceability closeness (+{dance_points:.2f})")

    return score, reasons

@dataclass
class Song:
    """Represents a song and its attributes."""
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
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """OOP implementation of the recommendation logic."""
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }
        scored_songs = sorted(
            ((song, score_song(user_prefs, song.__dict__)[0]) for song in self.songs),
            key=lambda item: item[1],
            reverse=True,
        )
        return [song for song, _ in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }
        score, reasons = score_song(user_prefs, song.__dict__)
        reason_text = ", ".join(reasons) if reasons else "no direct feature match"
        return f"Score {score:.2f} because {reason_text}."

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dictionaries."""
    songs: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            song: Dict[str, Any] = {}
            for key, value in row.items():
                if key in NUMERIC_FIELDS and value != "":
                    if key == "id":
                        song[key] = int(value)
                    elif key in {"tempo_bpm"}:
                        song[key] = int(float(value))
                    else:
                        song[key] = float(value)
                else:
                    song[key] = value
            songs.append(song)

    print(f"Loaded songs: {len(songs)}")
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return the top k recommendations."""
    scored_songs: List[Tuple[Dict[str, Any], float, List[str]]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, reasons))

    ranked_songs = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    recommendations: List[Tuple[Dict[str, Any], float, str]] = []
    for song, score, reasons in ranked_songs[:k]:
        explanation = "; ".join(reasons) if reasons else "no strong feature matches"
        recommendations.append((song, score, explanation))
    return recommendations
