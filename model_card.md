# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

VibeFinder 1.0

---

## 2. Goal / Task

This model suggests songs from a small catalog based on user taste.
It predicts what songs are most likely to match a user's preferred vibe.
The main goal is classroom learning, not production use.

---

## 3. Data Used

The dataset has 10 songs from `data/songs.csv`.
Each song includes title, artist, genre, mood, energy, tempo, danceability, and other audio-style fields.
The data is very small, so it cannot represent all music tastes.
Some genres and moods appear more often than others.

---

## 4. Algorithm Summary

The model gives points to each song, then ranks songs by total score.
Genre match adds +1.0 point.
Mood match adds +1.0 point.
Energy closeness can add up to +4.0 points, so songs near the target energy get rewarded most.
Small optional bonuses can be added for tempo or danceability if those targets are provided.

---

## 5. Observed Behavior / Biases

The model often favors songs with close energy values, even if mood is not perfect.
This can create a filter bubble around energetic songs for high-energy users.
Because the catalog is small, repeated styles like pop and lofi can dominate results.
The model does not use lyrics, language, or context, so recommendations are limited.

---

## 6. Evaluation Process

I tested four profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, and Conflicting Energy-Sad.
I compared top-5 outputs and checked whether they matched my intuition.
Main matches were strong: Sunrise City for pop, Library Rain for lofi, and Storm Runner for intense rock.
The surprise was the conflicting profile: high-energy songs still ranked high even with a mood mismatch.
This showed energy has the biggest influence in the current scoring setup.

---

## 7. Intended Use and Non-Intended Use

Intended use: a transparent, CLI-first classroom simulation to understand recommender basics.
Intended use: quick experiments with simple user profiles and scoring weights.
Not intended: real-user personalization, music licensing decisions, or high-stakes product ranking.
Not intended: judging culture, identity, or emotional wellness from listening behavior.

---

## 8. Ideas for Improvement

1. Add a diversity rule so top results are not all from similar styles.
2. Add more songs and more balanced genre/mood coverage.
3. Tune weights automatically from feedback instead of fixed manual values.

---

## 9. Personal Reflection

My biggest learning moment was seeing how one weight change can shift the whole ranking.
AI tools helped me draft logic and test ideas faster, but I had to double-check outputs because one duplicate function accidentally overrode my real scoring code.
I was surprised that a simple point system still feels like a "smart" recommendation when the reasons are shown clearly.
If I extend this project, I would try a hybrid approach that balances energy fit, genre/mood fit, and recommendation diversity.
