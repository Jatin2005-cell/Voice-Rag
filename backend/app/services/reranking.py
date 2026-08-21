"""
backend/app/services/reranking.py
Configurable reranking abstraction.
Defaults to NoOpReranker (RERANKING_ENABLED=false) to maintain sub-200ms latency SLA.
"""

from typing import List, Optional
import os
import time
from .vector_store import SearchResult

class BaseReranker:
    def rerank(self, query: str, results: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        raise NotImplementedError


class NoOpReranker(BaseReranker):
    """Pass-through reranker with 0ms latency."""
    def rerank(self, query: str, results: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        return results[:top_k]


class FastKeywordMatchReranker(BaseReranker):
    """
    Lightweight, fast lexical-dense hybrid boost reranker (sub-1ms).
    Boosts candidates that match key token overlaps from the query.
    """
    def rerank(self, query: str, results: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        query_words = set(query.lower().split())
        if not query_words or not results:
            return results[:top_k]

        scored = []
        for r in results:
            passage_words = set(r.text.lower().split())
            overlap = len(query_words.intersection(passage_words)) / max(1, len(query_words))
            # Hybrid combined score: 80% vector similarity + 20% lexical overlap
            hybrid_score = (0.80 * r.score) + (0.20 * overlap)
            r.score = hybrid_score
            scored.append(r)

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]


def get_reranker(strategy: Optional[str] = None) -> BaseReranker:
    enabled = os.getenv("RERANKING_ENABLED", "false").lower() in ("true", "1", "yes")
    strat = (strategy or os.getenv("RERANKER_STRATEGY", "none")).lower()
    
    if not enabled or strat == "none":
        return NoOpReranker()
    elif strat in ("keyword", "hybrid", "fast"):
        return FastKeywordMatchReranker()
    else:
        return NoOpReranker()
