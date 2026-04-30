# Reflection

The strongest result was how clearly the recommender separated the three main listening vibes. The pop profile consistently favored bright songs like "Sunrise City" and "Rooftop Lights," while the lofi profile shifted toward "Library Rain" and "Midnight Coding" because genre, mood, and acoustic texture lined up together.

The rock profile behaved differently again. "Storm Runner" kept rising because the higher energy and heavier genre matched the profile in more than one way, which showed that the scoring rule was not just following genre labels. That made the recommendations feel more believable than a single-feature sort.

The biggest surprise was how much the texture hint mattered for the chill profile. Once the parser recognized words like "acoustic" and "studying," it pushed softer songs higher and made the shortlist feel closer to a real playlist suggestion. That was a good example of the project extending beyond the original recommender rather than just ranking songs.

The main limitation is still the catalog size. A tiny set of songs means the system can only show a narrow slice of styles, so diversity checks are important. If I extended this again, I would add more songs and learn the weights from feedback instead of tuning them by hand.
 
What I changed while extending the project
- Implemented a lightweight RAG-style search over song metadata (TF‑IDF + cosine similarity) and added a fuzzy fallback so queries tolerate typos and partial keywords.
- Expanded the catalog from ~10 to ~50 songs to give retrieval and ranking more variety.
- Added compact play buttons in the UI that open a YouTube search for the selected song (a placeholder preview mechanism until direct preview URLs are available).
- Hardened the code with tests and small smoke scripts to validate retrieval behavior.

Lessons and next steps
- The retrieval-first approach makes the system easier to evaluate and explain because the shortlist is grounded in metadata matches before scoring.
- Short catalogs still constrain realism; adding more metadata and audio previews would let the system be judged more fairly.
- Next steps I would implement if I continued:
	- Add a small evaluation harness that runs the system on a fixed set of test prompts and prints aggregated metrics (coverage, ranking agreement, pass/fail thresholds).
	- Add preview URLs or a lightweight API to serve short audio previews rather than opening a search page.
	- Prototype an agentic workflow for multi-step recommendations (explicit planning + intermediate tool calls) and surface its decision trace for grading.
	- Experiment with few-shot or synthetic fine-tuning of a lightweight model for a specific style if a richer dataset becomes available.

Overall, the extension keeps the original recommender’s core idea while adding retrieval, explainability, and more robust UI/validation that make it demonstrably an AI-driven extension of the module-3 project.
