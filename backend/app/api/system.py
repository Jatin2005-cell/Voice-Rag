"""
backend/app/api/system.py
System architecture and configuration info endpoint.
"""

from fastapi import APIRouter
from ..config import settings
from ..schemas.response import SystemInfoResponse
from ..services.vector_store import get_vector_store

router = APIRouter()

@router.get("/system/info", response_model=SystemInfoResponse)
def get_system_info():
    store = get_vector_store()
    return SystemInfoResponse(
        project_name=settings.PROJECT_NAME,
        tagline=settings.TAGLINE,
        dataset_name=settings.DATASET_NAME,
        dataset_language=settings.DATASET_LANGUAGE,
        dataset_split=settings.DATASET_SPLIT,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        embedding_model=settings.EMBEDDING_MODEL,
        vector_store="FastDenseVectorStore (In-Memory BLAS/NumPy Cosine Matrix)",
        llm_provider=settings.LLM_PROVIDER,
        llm_model=settings.LLM_MODEL,
        stt_provider=settings.STT_PROVIDER,
        chunking_strategy=settings.CHUNKING_STRATEGY,
        top_k=settings.TOP_K,
        similarity_threshold=settings.SIMILARITY_THRESHOLD,
        reranking_enabled=settings.RERANKING_ENABLED,
        latency_target_ms=settings.LATENCY_TARGET_MS,
        indexed_chunks=store.count()
    )
