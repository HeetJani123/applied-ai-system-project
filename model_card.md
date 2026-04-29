# Model Card: Music Recommender+

## 1. Model Name

VibeFinder 2.0

---

## 2. Goal / Task

This model suggests songs from a small catalog based on a listening vibe.
It predicts what songs are most likely to match a user's preferred genre, mood, energy, tempo, and texture.
The main goal is classroom learning and demonstrating an extension of the original music recommender project.

---

## 3. Data Used

The dataset has 10 songs from [data/songs.csv](data/songs.csv).
Each song includes title, artist, genre, mood, energy, tempo, danceability, valence, and acousticness.
The data is very small, so it cannot represent all music tastes.
Some genres and moods appear more often than others, which makes the catalog slightly biased toward a few styles.

---

## 4. Algorithm Summary

The model first parses a freeform vibe description into preferences.
Genre match adds +2.0 points.
Mood match adds +1.5 points.
Energy closeness can add up to +2.5 points, so songs near the target energy get rewarded most.
Tempo, danceability, and acoustic or electronic texture add smaller bonuses when the profile mentions them.

---

## 5. Observed Behavior / Biases

The model often favors songs with close energy values, even if mood is not perfect.
This can create a filter bubble around energetic songs for high-energy users.
Because the catalog is small, repeated styles like pop and lofi can dominate results.
The model does not use lyrics, listening history, or user feedback, so recommendations are limited.

---

## 6. Evaluation Process

I tested three profiles: High-Energy Pop, Chill Lofi, and Deep Intense Rock.
I compared top-5 outputs and checked whether they matched my intuition.
Main matches were strong: Sunrise City for pop, Library Rain for lofi, and Storm Runner for intense rock.
The surprise was that the lofi profile preferred acoustic songs strongly, so texture mattered almost as much as genre and mood.
This showed the freeform parser is useful, but energy still has the biggest influence in the current scoring setup.

---

## 7. Intended Use and Non-Intended Use

Intended use: a transparent, CLI-first classroom simulation to understand recommender basics.
Intended use: quick experiments with simple user profiles, scoring weights, and explanations.
Not intended: real-user personalization, music licensing decisions, or high-stakes product ranking.
Not intended: judging culture, identity, or emotional wellness from listening behavior.

---

## 8. Ideas for Improvement

1. Add a diversity rule so top results are not all from similar styles.
2. Add more songs and more balanced genre and mood coverage.
3. Tune weights automatically from feedback instead of fixed manual values.

---

## 9. Personal Reflection

My biggest learning moment was seeing how one weight change can shift the whole ranking.
AI tools helped me draft the parser and testing ideas faster, but I still had to check the catalog behavior by hand because the weights can overemphasize one feature.
I was surprised that a simple point system still feels like a "smart" recommendation when the reasons are shown clearly.
If I extend this project again, I would try a hybrid approach that balances energy fit, genre and mood fit, acoustic texture, and recommendation diversity.
