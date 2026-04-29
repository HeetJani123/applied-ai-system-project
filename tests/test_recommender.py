import pytest

from src.recommender import analyze_listening_profile, infer_listening_profile, load_songs, recommend_songs


def test_recommend_songs_prioritizes_matching_pop_profile():
    profile = infer_listening_profile("Bright pop and happy workout energy.")
    songs = load_songs()

    results = recommend_songs(profile, songs, k=3)

    assert results
    assert results[0].song.title == "Sunrise City"
    assert results[0].song.genre == "pop"
    assert results[0].score >= results[1].score


def test_analyze_listening_profile_generates_grounded_recommendations():
    analysis = analyze_listening_profile("Chill lofi focus music for studying late at night with soft, acoustic textures.")

    assert analysis.profile.favorite_genre == "lofi"
    assert analysis.profile.favorite_mood == "chill"
    assert analysis.coverage_score > 0.5
    assert analysis.checks["has_recommendations"] is True
    assert analysis.checks["has_coverage"] is True
    assert analysis.top_matches[0].song.title == "Library Rain"
    assert any("focus" in point.lower() or "study" in point.lower() for point in analysis.talking_points)


def test_analyze_listening_profile_is_deterministic_for_same_input():
    profile_text = "Deep intense rock with driving guitars, powerful energy, and a heavy sound."

    first = analyze_listening_profile(profile_text)
    second = analyze_listening_profile(profile_text)

    assert first == second


def test_analyze_listening_profile_rejects_empty_input():
    with pytest.raises(ValueError):
        analyze_listening_profile("")
