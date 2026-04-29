from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple
import csv
import logging
import re


logger = logging.getLogger(__name__)

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "songs.csv"

NUMERIC_FIELDS = {"id", "energy", "tempo_bpm", "valence", "danceability", "acousticness"}
KNOWN_GENRES = ["indie pop", "synthwave", "ambient", "lofi", "jazz", "rock", "pop"]
KNOWN_MOODS = ["focused", "happy", "chill", "relaxed", "moody", "intense"]
ENERGY_HINTS = {
    "high energy": 0.88,
    "energetic": 0.88,
    "upbeat": 0.82,
    "workout": 0.9,
    "intense": 0.92,
    "deep": 0.84,
    "driving": 0.86,
    "chill": 0.38,
    "calm": 0.32,
    "relaxed": 0.36,
    "focus": 0.42,
    "focused": 0.42,
    "moody": 0.58,
}
TEMPO_HINTS = {
    "fast": 148,
    "upbeat": 128,
    "workout": 132,
    "driving": 150,
    "slow": 74,
    "calm": 68,
    "relaxed": 84,
    "focus": 80,
    "lofi": 78,
    "ambient": 60,
}
DANCEABILITY_HINTS = {
    "dance": 0.86,
    "groove": 0.78,
    "club": 0.84,
    "focus": 0.58,
    "study": 0.56,
    "calm": 0.48,
    "relaxed": 0.52,
}
SOUND_HINTS = {
    "acoustic": "acoustic",
    "unplugged": "acoustic",
    "piano": "acoustic",
    "electronic": "electronic",
    "synth": "electronic",
    "neon": "electronic",
}


@dataclass(frozen=True)
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: int
    valence: float
    danceability: float
    acousticness: float


@dataclass(frozen=True)
class ListeningProfile:
    name: str
    source_text: str
    favorite_genre: str | None = None
    favorite_mood: str | None = None
    target_energy: float | None = None
    target_tempo_bpm: int | None = None
    target_danceability: float | None = None
    sound_preference: str | None = None


@dataclass
class SongRecommendation:
    song: Song
    score: float
    reasons: List[str]


@dataclass
class RecommendationAnalysis:
    profile: ListeningProfile
    top_matches: List[SongRecommendation]
    coverage_score: float
    diversity_score: float
    warnings: List[str] = field(default_factory=list)
    checks: Dict[str, bool] = field(default_factory=dict)
    summary: str = ""
    talking_points: List[str] = field(default_factory=list)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _matches_phrase(preference: str | None, value: str) -> bool:
    if not preference:
        return False
    preference_text = _normalize_text(preference)
    value_text = _normalize_text(value)
    return preference_text == value_text or preference_text in value_text or value_text in preference_text


def _first_matching_phrase(text: str, phrases: Sequence[str]) -> str | None:
    normalized = _normalize_text(text)
    for phrase in sorted(phrases, key=len, reverse=True):
        if phrase in normalized:
            return phrase
    return None


def _infer_numeric_hint(text: str, hints: Dict[str, float]) -> float | None:
    normalized = _normalize_text(text)
    for phrase, value in hints.items():
        if phrase in normalized:
            return value
    return None


def _infer_tempo_hint(text: str) -> int | None:
    normalized = _normalize_text(text)
    for phrase, value in TEMPO_HINTS.items():
        if phrase in normalized:
            return value
    return None


def _infer_danceability_hint(text: str) -> float | None:
    normalized = _normalize_text(text)
    for phrase, value in DANCEABILITY_HINTS.items():
        if phrase in normalized:
            return value
    return None


def _infer_sound_preference(text: str) -> str | None:
    normalized = _normalize_text(text)
    for phrase, sound_preference in SOUND_HINTS.items():
        if phrase in normalized:
            return sound_preference
    return None


def infer_listening_profile(profile_text: str) -> ListeningProfile:
    if not profile_text.strip():
        raise ValueError("profile_text must not be empty")

    lines = _split_lines(profile_text)
    profile_name = lines[0] if lines else "listening profile"
    favorite_genre = _first_matching_phrase(profile_text, KNOWN_GENRES)
    favorite_mood = _first_matching_phrase(profile_text, KNOWN_MOODS)
    target_energy = _infer_numeric_hint(profile_text, ENERGY_HINTS)
    target_tempo_bpm = _infer_tempo_hint(profile_text)
    target_danceability = _infer_danceability_hint(profile_text)
    sound_preference = _infer_sound_preference(profile_text)

    return ListeningProfile(
        name=profile_name,
        source_text=profile_text,
        favorite_genre=favorite_genre,
        favorite_mood=favorite_mood,
        target_energy=target_energy,
        target_tempo_bpm=target_tempo_bpm,
        target_danceability=target_danceability,
        sound_preference=sound_preference,
    )


def load_songs(csv_path: str | Path = DEFAULT_CATALOG_PATH) -> List[Song]:
    """Load songs from the project catalog."""
    songs: List[Song] = []
    with open(csv_path, newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            parsed: Dict[str, Any] = {}
            for key, value in row.items():
                if key in NUMERIC_FIELDS and value != "":
                    if key == "id":
                        parsed[key] = int(value)
                    elif key == "tempo_bpm":
                        parsed[key] = int(float(value))
                    else:
                        parsed[key] = float(value)
                else:
                    parsed[key] = value

            songs.append(
                Song(
                    id=parsed["id"],
                    title=parsed["title"],
                    artist=parsed["artist"],
                    genre=parsed["genre"],
                    mood=parsed["mood"],
                    energy=parsed["energy"],
                    tempo_bpm=parsed["tempo_bpm"],
                    valence=parsed["valence"],
                    danceability=parsed["danceability"],
                    acousticness=parsed["acousticness"],
                )
            )

    logger.info("Loaded %d songs from %s", len(songs), csv_path)
    return songs


def _score_closeness(actual: float, target: float, max_points: float, span: float) -> float:
    similarity = max(0.0, 1.0 - abs(actual - target) / span)
    return max_points * similarity


def score_song(profile: ListeningProfile, song: Song) -> Tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    if _matches_phrase(profile.favorite_genre, song.genre):
        score += 2.0
        reasons.append("genre match (+2.0)")

    if _matches_phrase(profile.favorite_mood, song.mood):
        score += 1.5
        reasons.append("mood match (+1.5)")

    if profile.target_energy is not None:
        energy_points = _score_closeness(song.energy, profile.target_energy, max_points=2.5, span=1.0)
        score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.2f})")

    if profile.target_tempo_bpm is not None:
        tempo_points = _score_closeness(song.tempo_bpm, profile.target_tempo_bpm, max_points=0.75, span=140.0)
        score += tempo_points
        reasons.append(f"tempo closeness (+{tempo_points:.2f})")

    if profile.target_danceability is not None:
        dance_points = _score_closeness(song.danceability, profile.target_danceability, max_points=0.5, span=1.0)
        score += dance_points
        reasons.append(f"danceability closeness (+{dance_points:.2f})")

    if profile.sound_preference == "acoustic":
        acoustic_points = 0.75 * song.acousticness
        score += acoustic_points
        reasons.append(f"acoustic texture match (+{acoustic_points:.2f})")
    elif profile.sound_preference == "electronic":
        electronic_points = 0.75 * (1.0 - song.acousticness)
        score += electronic_points
        reasons.append(f"electronic texture match (+{electronic_points:.2f})")

    return score, reasons


def retrieve_candidate_songs(profile: ListeningProfile, songs: Sequence[Song]) -> Tuple[List[Song], List[str]]:
    candidates: List[Song] = []
    for song in songs:
        signal_match = False
        if _matches_phrase(profile.favorite_genre, song.genre):
            signal_match = True
        if _matches_phrase(profile.favorite_mood, song.mood):
            signal_match = True
        if profile.sound_preference == "acoustic" and song.acousticness >= 0.55:
            signal_match = True
        if profile.sound_preference == "electronic" and song.acousticness <= 0.45:
            signal_match = True
        if profile.target_energy is not None and abs(song.energy - profile.target_energy) <= 0.28:
            signal_match = True
        if profile.target_tempo_bpm is not None and abs(song.tempo_bpm - profile.target_tempo_bpm) <= 40:
            signal_match = True
        if profile.target_danceability is not None and abs(song.danceability - profile.target_danceability) <= 0.22:
            signal_match = True

        if signal_match:
            candidates.append(song)

    warnings: List[str] = []
    if not candidates:
        warnings.append("No strong signal match was found, so the recommender scored the full catalog.")
        candidates = list(songs)

    return candidates, warnings


def recommend_songs(profile: ListeningProfile, songs: Sequence[Song], k: int = 5) -> List[SongRecommendation]:
    scored: List[SongRecommendation] = []
    for song in songs:
        score, reasons = score_song(profile, song)
        scored.append(SongRecommendation(song=song, score=score, reasons=reasons))

    scored.sort(key=lambda item: (-item.score, item.song.artist, item.song.title))
    return scored[:k]


def _coverage_score(profile: ListeningProfile, recommendations: Sequence[SongRecommendation]) -> float:
    top_songs = [item.song for item in recommendations]
    total_axes = 0
    hits = 0

    if profile.favorite_genre is not None:
        total_axes += 1
        if any(_matches_phrase(profile.favorite_genre, song.genre) for song in top_songs):
            hits += 1

    if profile.favorite_mood is not None:
        total_axes += 1
        if any(_matches_phrase(profile.favorite_mood, song.mood) for song in top_songs):
            hits += 1

    if profile.target_energy is not None:
        total_axes += 1
        if any(abs(song.energy - profile.target_energy) <= 0.18 for song in top_songs):
            hits += 1

    if profile.target_tempo_bpm is not None:
        total_axes += 1
        if any(abs(song.tempo_bpm - profile.target_tempo_bpm) <= 25 for song in top_songs):
            hits += 1

    if profile.target_danceability is not None:
        total_axes += 1
        if any(abs(song.danceability - profile.target_danceability) <= 0.12 for song in top_songs):
            hits += 1

    if profile.sound_preference is not None:
        total_axes += 1
        if profile.sound_preference == "acoustic" and any(song.acousticness >= 0.55 for song in top_songs):
            hits += 1
        if profile.sound_preference == "electronic" and any(song.acousticness <= 0.45 for song in top_songs):
            hits += 1

    return hits / max(1, total_axes)


def _diversity_score(recommendations: Sequence[SongRecommendation]) -> float:
    if not recommendations:
        return 0.0

    top_songs = [item.song for item in recommendations]
    unique_genres = len({song.genre for song in top_songs})
    unique_artists = len({song.artist for song in top_songs})
    possible = min(len(top_songs), 5)
    return min(1.0, (unique_genres + unique_artists) / (2.0 * possible))


def _build_talking_points(profile: ListeningProfile, recommendations: Sequence[SongRecommendation]) -> List[str]:
    talking_points: List[str] = []
    for item in recommendations[:3]:
        reason_preview = "; ".join(item.reasons[:2]) if item.reasons else "broad catalog fit"
        talking_points.append(
            f"Use {item.song.title} by {item.song.artist} as an anchor because it shows {reason_preview}."
        )

    if not talking_points:
        talking_points.append(
            f"Build the playlist around {profile.name.lower()} with a mix of genre, mood, and energy matches."
        )

    return talking_points


def analyze_listening_profile(
    profile_text: str,
    songs: Sequence[Song] | None = None,
    k: int = 5,
) -> RecommendationAnalysis:
    profile = infer_listening_profile(profile_text)
    catalog = list(songs) if songs is not None else load_songs()

    candidates, warnings = retrieve_candidate_songs(profile, catalog)
    recommendations = recommend_songs(profile, candidates, k=k)
    coverage_score = _coverage_score(profile, recommendations)
    diversity_score = _diversity_score(recommendations)

    checks = {
        "has_recommendations": bool(recommendations),
        "has_genre_fit": not profile.favorite_genre or any(
            _matches_phrase(profile.favorite_genre, item.song.genre) for item in recommendations
        ),
        "has_mood_fit": not profile.favorite_mood or any(
            _matches_phrase(profile.favorite_mood, item.song.mood) for item in recommendations
        ),
        "has_coverage": coverage_score >= 0.5,
        "has_diversity": diversity_score >= 0.35,
    }

    if not checks["has_coverage"]:
        warnings.append("The top songs cover only part of the requested vibe, so the shortlist may need refinement.")
    if not checks["has_diversity"]:
        warnings.append("The shortlist is narrow, so it may be too similar for a playlist mix.")

    summary = (
        f"Recommended {len(recommendations)} songs for {profile.name} with "
        f"{coverage_score:.0%} preference coverage and {diversity_score:.0%} diversity."
    )

    return RecommendationAnalysis(
        profile=profile,
        top_matches=list(recommendations),
        coverage_score=coverage_score,
        diversity_score=diversity_score,
        warnings=warnings,
        checks=checks,
        summary=summary,
        talking_points=_build_talking_points(profile, recommendations),
    )


class MusicRecommender:
    """Plan-act-check workflow for music recommendation support."""

    def __init__(self, songs: Sequence[Song], logger_instance: logging.Logger | None = None):
        self.songs = list(songs)
        self.logger = logger_instance or logger

    def analyze(self, profile_text: str, k: int = 5) -> RecommendationAnalysis:
        self.logger.info("Starting music recommendation analysis")
        return analyze_listening_profile(profile_text, self.songs, k=k)


def format_analysis(analysis: RecommendationAnalysis) -> str:
    lines = [
        f"Listening profile: {analysis.profile.name}",
        f"Coverage score: {analysis.coverage_score:.2f}",
        f"Diversity score: {analysis.diversity_score:.2f}",
        "",
        "Top matches:",
    ]

    for index, item in enumerate(analysis.top_matches, start=1):
        lines.append(f"{index}. {item.song.title} by {item.song.artist}")
        lines.append(f"   Genre: {item.song.genre} | Mood: {item.song.mood} | Score: {item.score:.2f}")
        lines.append(f"   Reasons: {'; '.join(item.reasons) if item.reasons else 'no direct feature match'}")

    lines.extend(["", "Playlist notes:"])
    for point in analysis.talking_points:
        lines.append(f"- {point}")

    if analysis.warnings:
        lines.extend(["", "Warnings:"])
        for warning in analysis.warnings:
            lines.append(f"- {warning}")

    lines.extend(["", "Checks:"])
    for check_name, passed in analysis.checks.items():
        lines.append(f"- {check_name}: {'pass' if passed else 'fail'}")

    return "\n".join(lines)
