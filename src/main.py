"""Command line runner for the music recommender extension."""

from __future__ import annotations

import logging
from textwrap import dedent

from src.recommender import analyze_listening_profile, format_analysis


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def print_analysis(label: str, profile_text: str) -> None:
    print(f"\n=== {label} ===\n")
    analysis = analyze_listening_profile(profile_text)
    print(format_analysis(analysis))


def main() -> None:
    scenarios = [
        (
            "High-Energy Pop",
            dedent(
                """
                Bright pop for a workout with happy hooks, fast tempo, and strong energy.
                """
            ).strip(),
        ),
        (
            "Chill Lofi",
            dedent(
                """
                Chill lofi focus music for studying late at night with soft, acoustic textures.
                """
            ).strip(),
        ),
        (
            "Deep Intense Rock",
            dedent(
                """
                Deep intense rock with driving guitars, powerful energy, and a heavy sound.
                """
            ).strip(),
        ),
    ]

    for label, profile_text in scenarios:
        print_analysis(label, profile_text)


if __name__ == "__main__":
    main()
