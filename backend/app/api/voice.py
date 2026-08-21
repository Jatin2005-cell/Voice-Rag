"""
backend/app/api/voice.py
Voice query RAG endpoint. Transcribes audio via STT and executes grounded RAG.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from ..schemas.response import RAGResponse
from ..services.orchestrator import get_orchestrator

router = APIRouter()

@router.post("/voice/query", response_model=RAGResponse)
async def handle_voice_query(
    file: UploadFile = File(...),
    language: Optional[str] = Form("hi"),
    top_k: Optional[int] = Form(5),
    min_score: Optional[float] = Form(None)
):
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio payload received.")

        orchestrator = get_orchestrator()
        result = orchestrator.process_voice_query(
            audio_bytes=audio_bytes,
            language=language or "hi",
            content_type=file.content_type or "audio/wav",
            top_k=top_k,
            min_score=min_score
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
