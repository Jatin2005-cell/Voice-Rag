"""
backend/app/schemas/query.py
Pydantic schemas for incoming queries and requests.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="User query text (e.g. Hindi or English question)")
    top_k: Optional[int] = Field(5, description="Number of passages to retrieve")
    min_score: Optional[float] = Field(None, description="Similarity cutoff threshold")
    language: Optional[str] = Field("hi", description="Target Indic language code")

class VoiceQueryMetadata(BaseModel):
    language: Optional[str] = "hi"
    top_k: Optional[int] = 5
    min_score: Optional[float] = None
