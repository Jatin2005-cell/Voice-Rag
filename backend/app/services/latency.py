"""
backend/app/services/latency.py
Granular latency instrumentation and aggregation utilities.
"""

from typing import Dict, Any, Optional
import time

class LatencyTracker:
    def __init__(self):
        self.embedding_ms: float = 0.0
        self.retrieval_ms: float = 0.0
        self.reranking_ms: float = 0.0
        self.context_building_ms: float = 0.0
        self.generation_ms: float = 0.0
        self.grounding_ms: float = 0.0
        self.total_rag_ms: float = 0.0
        self.stt_ms: Optional[float] = None
        self.end_to_end_ms: Optional[float] = None

    def compute_total(self):
        self.total_rag_ms = round(
            self.embedding_ms +
            self.retrieval_ms +
            self.reranking_ms +
            self.context_building_ms +
            self.generation_ms +
            self.grounding_ms,
            2
        )
        if self.stt_ms is not None:
            self.end_to_end_ms = round(self.stt_ms + self.total_rag_ms, 2)
        else:
            self.end_to_end_ms = self.total_rag_ms

    def to_dict(self) -> Dict[str, Any]:
        self.compute_total()
        d = {
            "embedding_ms": round(self.embedding_ms, 2),
            "retrieval_ms": round(self.retrieval_ms, 2),
            "reranking_ms": round(self.reranking_ms, 2),
            "context_building_ms": round(self.context_building_ms, 2),
            "generation_ms": round(self.generation_ms, 2),
            "grounding_ms": round(self.grounding_ms, 2),
            "total_rag_ms": round(self.total_rag_ms, 2)
        }
        if self.stt_ms is not None:
            d["stt_ms"] = round(self.stt_ms, 2)
            d["end_to_end_ms"] = round(self.end_to_end_ms, 2)
        return d
