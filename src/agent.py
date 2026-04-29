"""
Agentic workflow for music recommendation.

Uses multi-step reasoning with planning to decide which factors matter most
and how to rank songs. Tracks decisions and reasoning steps.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


class ReasoningStep(Enum):
    """Possible reasoning steps in the workflow."""
    PARSE_QUERY = "parse_query"
    PRIORITIZE_FACTORS = "prioritize_factors"
    RETRIEVE_CANDIDATES = "retrieve_candidates"
    SCORE_CANDIDATES = "score_candidates"
    APPLY_CONSTRAINTS = "apply_constraints"
    FINALIZE_RANKING = "finalize_ranking"


@dataclass
class DecisionLog:
    """Log of a single decision in the reasoning process."""
    step: ReasoningStep
    decision: str
    reasoning: str
    supporting_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Full response from the agent including reasoning trail."""
    final_ranking: List[Dict]  # Song recommendations
    decision_log: List[DecisionLog]  # Full reasoning trail
    confidence: float  # Confidence in the recommendation (0.0-1.0)
    
    def summary(self) -> str:
        """Generate a human-readable summary of the reasoning."""
        steps = [f"Step {i+1}: {log.step.value} - {log.decision}" for i, log in enumerate(self.decision_log)]
        return f"Confidence: {self.confidence:.2f}\n" + "\n".join(steps)


class MusicRecommendationAgent:
    """
    Agentic workflow for music recommendations.
    
    Multi-step reasoning process:
    1. Parse the user query to understand intent
    2. Prioritize factors (what matters most for this query?)
    3. Retrieve candidate songs via RAG
    4. Score candidates based on priorities
    5. Apply diversity/coverage constraints
    6. Finalize ranking and explain
    """
    
    def __init__(self, rag, recommender):
        """
        Initialize agent with RAG and recommender components.
        
        Args:
            rag: SongRAG instance for semantic search
            recommender: MusicRecommender instance for scoring
        """
        self.rag = rag
        self.recommender = recommender
        self.decision_log: List[DecisionLog] = []
    
    def reason(self, vibe_description: str, top_k: int = 5) -> AgentResponse:
        """
        Full agentic reasoning process.
        
        Args:
            vibe_description: User's vibe description
            top_k: Number of recommendations to return
        
        Returns:
            AgentResponse with reasoning trail
        """
        self.decision_log = []
        
        # Step 1: Parse query
        parsed = self._parse_query(vibe_description)
        self._log_decision(
            ReasoningStep.PARSE_QUERY,
            f"Parsed query into {len(parsed['key_terms'])} key terms",
            f"Identified: genre={parsed['inferred_genre']}, mood={parsed['inferred_mood']}, "
            f"energy_hint={parsed['energy_hint']}",
            parsed
        )
        
        # Step 2: Prioritize factors
        priorities = self._prioritize_factors(vibe_description, parsed)
        self._log_decision(
            ReasoningStep.PRIORITIZE_FACTORS,
            f"Prioritized factors: {priorities['order']}",
            f"Primary factor: {priorities['primary']}, "
            f"Weighting: {priorities['weight_distribution']}",
            priorities
        )
        
        # Step 3: Retrieve candidates
        candidates = self._retrieve_candidates(vibe_description, parsed)
        self._log_decision(
            ReasoningStep.RETRIEVE_CANDIDATES,
            f"Retrieved {len(candidates)} candidate songs",
            f"Used semantic search + genre/mood matching. "
            f"Sources: {len(candidates['semantic'])} semantic, "
            f"{len(candidates['genre'])} genre-match, "
            f"{len(candidates['mood'])} mood-match",
            candidates
        )
        
        # Step 4: Score candidates
        scored = self._score_candidates(candidates, parsed, priorities)
        self._log_decision(
            ReasoningStep.SCORE_CANDIDATES,
            f"Scored {len(scored)} candidates using {priorities['primary']} as primary factor",
            f"Top candidate: {scored[0]['title']} (score: {scored[0]['score']:.2f})",
            {"top_3_scores": [s['score'] for s in scored[:3]]}
        )
        
        # Step 5: Apply constraints
        constrained = self._apply_constraints(scored, top_k)
        self._log_decision(
            ReasoningStep.APPLY_CONSTRAINTS,
            f"Applied diversity/coverage constraints, final count: {len(constrained)}",
            f"Filtered {len(scored) - len(constrained)} songs for diversity. "
            f"Genres: {set(s['genre'] for s in constrained)}",
            {"final_genres": list(set(s['genre'] for s in constrained))}
        )
        
        # Step 6: Finalize
        confidence = self._calculate_confidence(constrained, parsed)
        self._log_decision(
            ReasoningStep.FINALIZE_RANKING,
            f"Finalized ranking with confidence {confidence:.2f}",
            f"Coverage check: {self._coverage_status(constrained, parsed)}",
            {"confidence": confidence}
        )
        
        return AgentResponse(
            final_ranking=constrained,
            decision_log=self.decision_log,
            confidence=confidence
        )
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse user query to extract intent and key terms."""
        query_lower = query.lower()
        
        key_terms = set()
        for word in query_lower.split():
            if len(word) > 3:
                key_terms.add(word)
        
        # Infer genre
        genre_keywords = {
            'pop': ['pop', 'pop'],
            'rock': ['rock', 'rock', 'heavy', 'guitar'],
            'lofi': ['lofi', 'lo-fi', 'chill', 'study'],
            'jazz': ['jazz', 'smooth'],
            'electronic': ['electronic', 'synth', 'edm']
        }
        inferred_genre = None
        for genre, keywords in genre_keywords.items():
            if any(kw in query_lower for kw in keywords):
                inferred_genre = genre
                break
        
        # Infer mood
        mood_keywords = {
            'happy': ['happy', 'bright', 'upbeat', 'cheerful', 'joyful'],
            'chill': ['chill', 'calm', 'relaxing', 'peaceful'],
            'intense': ['intense', 'powerful', 'dark', 'deep', 'serious'],
            'melancholic': ['sad', 'melancholic', 'nostalgic', 'slow']
        }
        inferred_mood = None
        for mood, keywords in mood_keywords.items():
            if any(kw in query_lower for kw in keywords):
                inferred_mood = mood
                break
        
        # Infer energy hint
        energy_hint = 'medium'
        if any(word in query_lower for word in ['fast', 'high', 'energetic', 'intense', 'workout']):
            energy_hint = 'high'
        elif any(word in query_lower for word in ['slow', 'low', 'chill', 'relax', 'study']):
            energy_hint = 'low'
        
        return {
            'key_terms': list(key_terms),
            'inferred_genre': inferred_genre,
            'inferred_mood': inferred_mood,
            'energy_hint': energy_hint,
            'query': query
        }
    
    def _prioritize_factors(self, query: str, parsed: Dict) -> Dict[str, Any]:
        """Decide which factors to prioritize based on query."""
        query_lower = query.lower()
        
        # Determine primary focus
        primary = 'genre'
        if any(w in query_lower for w in ['feel', 'mood', 'vibe', 'emotional']):
            primary = 'mood'
        elif any(w in query_lower for w in ['energy', 'intense', 'workout', 'relax']):
            primary = 'energy'
        elif any(w in query_lower for w in ['tempo', 'fast', 'slow']):
            primary = 'tempo'
        
        # Define weighting order
        if primary == 'genre':
            order = ['genre', 'mood', 'energy', 'tempo', 'texture']
            weights = {'genre': 2.0, 'mood': 1.5, 'energy': 2.0, 'tempo': 0.75, 'texture': 0.75}
        elif primary == 'mood':
            order = ['mood', 'genre', 'energy', 'texture', 'tempo']
            weights = {'mood': 2.0, 'genre': 1.5, 'energy': 1.5, 'texture': 1.0, 'tempo': 0.5}
        elif primary == 'energy':
            order = ['energy', 'genre', 'mood', 'texture', 'tempo']
            weights = {'energy': 2.5, 'genre': 1.5, 'mood': 1.0, 'texture': 0.75, 'tempo': 1.0}
        else:  # tempo or texture
            order = ['tempo', 'energy', 'genre', 'mood', 'texture']
            weights = {'tempo': 2.0, 'energy': 2.0, 'genre': 1.5, 'mood': 1.0, 'texture': 1.0}
        
        return {
            'primary': primary,
            'order': order,
            'weight_distribution': weights
        }
    
    def _retrieve_candidates(self, query: str, parsed: Dict) -> Dict[str, List[str]]:
        """Retrieve candidate songs using multiple strategies."""
        semantic_results = self.rag.search(query, top_k=10)
        semantic_ids = [song_id for song_id, _ in semantic_results]
        
        genre_ids = []
        if parsed['inferred_genre']:
            genre_ids = self.rag.search_by_genre(parsed['inferred_genre'], top_k=10)
        
        mood_ids = []
        if parsed['inferred_mood']:
            mood_ids = self.rag.search_by_mood(parsed['inferred_mood'], top_k=10)
        
        # Combine and deduplicate
        all_ids = list(set(semantic_ids + genre_ids + mood_ids))
        
        return {
            'semantic': semantic_ids,
            'genre': genre_ids,
            'mood': mood_ids,
            'combined': all_ids
        }
    
    def _score_candidates(self, candidates: Dict, parsed: Dict, priorities: Dict) -> List[Dict]:
        """Score candidate songs using recommender."""
        # Create a synthetic profile to pass to recommender
        profile_text = parsed['query']
        profile = self.recommender.infer_listening_profile(profile_text)
        
        songs_df = self.recommender.songs_df
        scored = []
        
        for song_id in candidates['combined']:
            try:
                song_row = songs_df[songs_df['id'] == int(song_id)].iloc[0]
                song = self.recommender.Song(**song_row.to_dict())
                score, reasons = self.recommender.score_song(profile, song)
                scored.append({
                    'id': str(song.id),
                    'title': song.title,
                    'artist': song.artist,
                    'genre': song.genre,
                    'mood': song.mood,
                    'energy': song.energy,
                    'score': score,
                    'reasons': reasons
                })
            except:
                pass
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored
    
    def _apply_constraints(self, scored: List[Dict], top_k: int) -> List[Dict]:
        """Apply diversity constraints to ensure varied playlist."""
        selected = []
        genres_seen = set()
        artists_seen = set()
        
        for song in scored:
            # Prefer new genres
            if song['genre'] not in genres_seen or len(selected) < top_k:
                if song['artist'] not in artists_seen or len(selected) < top_k:
                    selected.append(song)
                    genres_seen.add(song['genre'])
                    artists_seen.add(song['artist'])
                    
                    if len(selected) >= top_k:
                        break
        
        return selected
    
    def _calculate_confidence(self, ranked: List[Dict], parsed: Dict) -> float:
        """Calculate confidence in the recommendation."""
        if not ranked:
            return 0.0
        
        # Base confidence on top score and variety
        top_score = ranked[0]['score']
        confidence = min(top_score / 10.0, 1.0)  # Normalize to 0-1
        
        # Reduce confidence if inferred genre/mood didn't match well
        genre_match = any(s['genre'] == parsed['inferred_genre'] for s in ranked) if parsed['inferred_genre'] else True
        mood_match = any(s['mood'] == parsed['inferred_mood'] for s in ranked) if parsed['inferred_mood'] else True
        
        if not genre_match or not mood_match:
            confidence *= 0.7
        
        return confidence
    
    def _coverage_status(self, ranked: List[Dict], parsed: Dict) -> str:
        """Generate text description of coverage."""
        genres = set(s['genre'] for s in ranked)
        has_genre = parsed['inferred_genre'] in genres if parsed['inferred_genre'] else True
        has_mood = any(s['mood'] == parsed['inferred_mood'] for s in ranked) if parsed['inferred_mood'] else True
        
        return f"Genre coverage: {'✓' if has_genre else '✗'}, Mood coverage: {'✓' if has_mood else '✗'}"
    
    def _log_decision(self, step: ReasoningStep, decision: str, reasoning: str, data: Dict):
        """Log a reasoning step."""
        self.decision_log.append(
            DecisionLog(
                step=step,
                decision=decision,
                reasoning=reasoning,
                supporting_data=data
            )
        )
