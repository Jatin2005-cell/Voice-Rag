"""
backend/app/services/retrieval.py
Core dense retrieval pipeline with relevance filtering and stage latency measurement.
"""

from typing import List, Dict, Any, Optional
import time
from .embeddings import get_embedding_provider, EmbeddingProvider
from .vector_store import get_vector_store, VectorStore, SearchResult
from .reranking import get_reranker, BaseReranker

class RetrievalPipeline:
    def __init__(
        self,
        embedder: Optional[EmbeddingProvider] = None,
        vector_store: Optional[VectorStore] = None,
        reranker: Optional[BaseReranker] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.35,
        reranking_enabled: bool = False
    ):
        self.embedder = embedder or get_embedding_provider()
        self.vector_store = vector_store or get_vector_store()
        self.reranker = reranker or get_reranker()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.reranking_enabled = reranking_enabled

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> Dict[str, Any]:
        k = top_k if top_k is not None else self.top_k
        threshold = min_score if min_score is not None else self.similarity_threshold

        t_start = time.perf_counter()

        # Step 1: Query Embedding
        t_emb_start = time.perf_counter()
        query_vector = self.embedder.embed_text(query)
        emb_ms = (time.perf_counter() - t_emb_start) * 1000.0

        # Step 2: Vector Search
        t_search_start = time.perf_counter()
        search_results: List[SearchResult] = self.vector_store.similarity_search(
            query_embedding=query_vector,
            top_k=k * 2 if self.reranking_enabled else k,
            min_score=0.0
        )
        search_ms = (time.perf_counter() - t_search_start) * 1000.0

        # Step 3: Optional Reranking
        t_rerank_start = time.perf_counter()
        if self.reranking_enabled and search_results:
            search_results = self.reranker.rerank(query, search_results, top_k=k)
        rerank_ms = (time.perf_counter() - t_rerank_start) * 1000.0

        # Step 4: Relevance Filtering
        filtered_results = [r for r in search_results if r.score >= threshold][:k]
        
        total_retrieval_ms = (time.perf_counter() - t_start) * 1000.0

        return {
            "query": query,
            "results": filtered_results,
            "all_candidates": search_results[:k],
            "passed_threshold": len(filtered_results) > 0,
            "top_score": search_results[0].score if search_results else 0.0,
            "latency": {
                "embedding_ms": round(emb_ms, 2),
                "retrieval_ms": round(search_ms, 2),
                "reranking_ms": round(rerank_ms, 2),
                "total_retrieval_ms": round(total_retrieval_ms, 2)
            }
        }
