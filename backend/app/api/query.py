"""
backend/app/api/query.py
Text query RAG endpoint.
"""

from fastapi import APIRouter, HTTPException
from ..schemas.query import QueryRequest
from ..schemas.response import RAGResponse
from ..services.orchestrator import get_orchestrator

router = APIRouter()

@router.post("/query", response_model=RAGResponse)
def handle_query(req: QueryRequest):
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.run_rag_pipeline(
            query=req.query,
            top_k=req.top_k,
            min_score=req.min_score
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
