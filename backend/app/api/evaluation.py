"""
backend/app/api/evaluation.py
Retrieval and Latency evaluation metrics API endpoints.
Serves real evaluation summary and detailed distribution results.
"""

from fastapi import APIRouter, HTTPException
import os
import json
from ..config import settings

router = APIRouter()

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "evaluation", "results"))

@router.get("/evaluation/summary")
def get_evaluation_summary():
    summary_path = os.path.join(RESULTS_DIR, "summary.json")
    if not os.path.exists(summary_path):
        return {
            "status": "not_evaluated",
            "message": "Evaluation suite not yet executed. Run python evaluation/run_retrieval_eval.py and python evaluation/run_latency.py.",
            "dataset_name": settings.DATASET_NAME,
            "language": settings.DATASET_LANGUAGE,
            "target_latency_ms": settings.LATENCY_TARGET_MS
        }

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read evaluation summary: {e}")

@router.get("/evaluation/latency")
def get_latency_details():
    latency_path = os.path.join(RESULTS_DIR, "latency_results.json")
    if not os.path.exists(latency_path):
        raise HTTPException(status_code=404, detail="Latency results not found.")
    with open(latency_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/evaluation/retrieval")
def get_retrieval_details():
    retrieval_path = os.path.join(RESULTS_DIR, "retrieval_results.json")
    if not os.path.exists(retrieval_path):
        raise HTTPException(status_code=404, detail="Retrieval results not found.")
    with open(retrieval_path, "r", encoding="utf-8") as f:
        return json.load(f)
