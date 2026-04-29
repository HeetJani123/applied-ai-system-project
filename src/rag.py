"""
RAG (Retrieval-Augmented Generation) module for semantic song search.

Indexes songs by metadata and allows querying by semantic similarity.
Uses TF-IDF vectorization for efficient candidate retrieval.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


@dataclass
class SongMetadata:
    """Rich metadata for a song for semantic indexing."""
    id: str
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    # Constructed searchable text combining all metadata
    searchable_text: str


class SongRAG:
    """
    Retrieval-Augmented Generation for songs.
    
    Indexes songs and allows semantic search based on descriptions,
    mood queries, genre queries, and combined natural language queries.
    """
    
    def __init__(self, songs_df: pd.DataFrame):
        """Initialize RAG with songs data."""
        self.songs_df = songs_df.copy()
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=100
        )
        self._build_index()
    
    def _build_index(self):
        """Build TF-IDF index for all songs."""
        # Create searchable text combining title, artist, genre, mood
        searchable_texts = []
        for _, row in self.songs_df.iterrows():
            # Combine all metadata with repeating key terms for weight
            text = f"{row['title']} {row['artist']} {row['genre']} {row['mood']} " \
                   f"genre:{row['genre']} mood:{row['mood']} " \
                   f"energy:{self._describe_energy(row['energy'])} " \
                   f"tempo:{self._describe_tempo(row['tempo_bpm'])} " \
                   f"acoustic:{row['acousticness']:.1f} "
            searchable_texts.append(text)
        
        self.searchable_texts = searchable_texts
        # Fit vectorizer and transform
        self.tfidf_matrix = self.vectorizer.fit_transform(searchable_texts)
        
        # Also build metadata objects for quick access
        self.metadata = [
            SongMetadata(
                id=str(row['id']),
                title=row['title'],
                artist=row['artist'],
                genre=row['genre'],
                mood=row['mood'],
                energy=row['energy'],
                searchable_text=text
            )
            for (_, row), text in zip(self.songs_df.iterrows(), searchable_texts)
        ]
    
    @staticmethod
    def _describe_energy(energy: float) -> str:
        """Convert energy value to descriptive terms."""
        if energy < 0.3:
            return "low calm relaxing"
        elif energy < 0.6:
            return "medium moderate balanced"
        else:
            return "high energetic intense"
    
    @staticmethod
    def _describe_tempo(tempo: float) -> str:
        """Convert tempo to descriptive terms."""
        if tempo < 90:
            return "slow leisurely"
        elif tempo < 120:
            return "moderate steady"
        else:
            return "fast upbeat"
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for songs by semantic similarity.
        
        Args:
            query: Natural language query (e.g., "upbeat pop for running")
            top_k: Number of results to return
        
        Returns:
            List of (song_id, similarity_score) tuples, sorted by relevance
        """
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Compute similarity to all songs
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return song IDs and scores
        results = []
        for idx in top_indices:
            song_id = str(self.songs_df.iloc[idx]['id'])
            score = float(similarities[idx])
            results.append((song_id, score))
        
        return results
    
    def search_by_genre(self, genre: str, top_k: int = 5) -> List[str]:
        """Search songs by exact genre match."""
        matching = self.songs_df[self.songs_df['genre'].str.lower() == genre.lower()]
        if len(matching) == 0:
            # Fallback to partial match
            matching = self.songs_df[self.songs_df['genre'].str.lower().str.contains(genre.lower())]
        return [str(row['id']) for _, row in matching.head(top_k).iterrows()]
    
    def search_by_mood(self, mood: str, top_k: int = 5) -> List[str]:
        """Search songs by exact mood match."""
        matching = self.songs_df[self.songs_df['mood'].str.lower() == mood.lower()]
        if len(matching) == 0:
            # Fallback to partial match
            matching = self.songs_df[self.songs_df['mood'].str.lower().str.contains(mood.lower())]
        return [str(row['id']) for _, row in matching.head(top_k).iterrows()]
    
    def search_by_energy_range(self, min_energy: float, max_energy: float, top_k: int = 5) -> List[str]:
        """Search songs within an energy range."""
        matching = self.songs_df[
            (self.songs_df['energy'] >= min_energy) & 
            (self.songs_df['energy'] <= max_energy)
        ]
        return [str(row['id']) for _, row in matching.head(top_k).iterrows()]
    
    def get_metadata(self, song_id: str) -> Dict:
        """Get full metadata for a song."""
        song = self.songs_df[self.songs_df['id'] == int(song_id)]
        if len(song) == 0:
            return None
        row = song.iloc[0]
        return row.to_dict()
    
    def get_similar_songs(self, song_id: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Find songs similar to a given song."""
        if int(song_id) not in self.songs_df['id'].values:
            return []
        
        # Get metadata for the reference song
        ref_song = self.songs_df[self.songs_df['id'] == int(song_id)].iloc[0]
        query = f"genre:{ref_song['genre']} mood:{ref_song['mood']} " \
                f"energy:{self._describe_energy(ref_song['energy'])}"
        
        # Search and exclude the reference song
        results = self.search(query, top_k=top_k + 1)
        results = [r for r in results if r[0] != song_id][:top_k]
        
        return results
