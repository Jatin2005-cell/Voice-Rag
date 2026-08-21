"""
backend/app/schemas/response.py
Pydantic schemas for standardized API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LatencyBreakdown(BaseModel):
    embedding_ms: float = 0.0
    retrieval_ms: float = 0.0
    reranking_ms: float = 0.0
    context_building_ms: float = 0.0
    generation_ms: float = 0.0
    grounding_ms: float = 0.0
    total_rag_ms: float = 0.0
    stt_ms: Optional[float] = None
    end_to_end_ms: Optional[float] = None

class SourcePassage(BaseModel):
    chunk_id: str
    query_id: int
    passage_idx: int
    score: float
    text: str
    english_text: Optional[str] = ""
    language: str
    is_selected: int = 0
    strategy: str = "passage_aware"
    metadata: Optional[Dict[str, Any]] = None

class RAGResponse(BaseModel):
    query: str
    transcript: str
    answer: str
    grounded: bool
    confidence: float
    sources: List[Dict[str, Any]]
    guardrail: Dict[str, Any]
    latency: LatencyBreakdown
    why_this_answer: Optional[Dict[str, Any]] = None
    stt_provider: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    project: str
    tagline: str
    version: str
    indexed_chunks: int
    dimension: int
    vector_store_status: str

class SystemInfoResponse(BaseModel):
    project_name: str
    tagline: str
    dataset_name: str
    dataset_language: str
    dataset_split: str
    embedding_provider: str
    embedding_model: str
    vector_store: str
    llm_provider: str
    llm_model: str
    stt_provider: str
    chunking_strategy: str
    top_k: int
    similarity_threshold: float
    reranking_enabled: bool
    latency_target_ms: float
    indexed_chunks: int
