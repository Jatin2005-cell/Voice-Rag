"""
backend/app/api/health.py
Health check and readiness endpoint.
"""

from fastapi import APIRouter
from ..config import settings
from ..services.vector_store import get_vector_store
from ..schemas.response import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    store = get_vector_store()
    h = store.health()
    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        tagline=settings.TAGLINE,
        version=settings.VERSION,
        indexed_chunks=h.get("indexed_chunks", 0),
        dimension=h.get("dimension", 384),
        vector_store_status=h.get("status", "empty")
    )
