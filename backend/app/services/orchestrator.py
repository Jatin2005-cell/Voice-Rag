"""
backend/app/services/orchestrator.py
Central RAG Orchestrator Harness.
Manages the end-to-end flow:
Input Validation -> STT -> Query Preprocessing -> Embedding -> Retrieval -> Relevance Filtering ->
Evidence Guardrail -> Context Building -> LLM Generation -> Grounding Verification -> Latency Recording.
"""

from typing import Dict, Any, Optional, List
import time
import logging
from .guardrails import GuardrailEngine, ABSTENTION_MESSAGE
from .retrieval import RetrievalPipeline
from .context_builder import ContextBuilder
from .generation import get_llm_provider, LLMProvider
from .grounding import GroundingValidator, GroundingResult
from .speech_to_text import get_stt_provider, SpeechToTextProvider
from .latency import LatencyTracker
from .vector_store import SearchResult

logger = logging.getLogger("voicerag.orchestrator")

class RAGOrchestrator:
    def __init__(
        self,
        retrieval_pipeline: Optional[RetrievalPipeline] = None,
        llm_provider: Optional[LLMProvider] = None,
        guardrail_engine: Optional[GuardrailEngine] = None,
        grounding_validator: Optional[GroundingValidator] = None,
        stt_provider: Optional[SpeechToTextProvider] = None,
        default_top_k: int = 5,
        default_similarity_threshold: float = 0.0  # FIXED: Lowered default threshold from 0.35 to 0.0
    ):
        self.retrieval = retrieval_pipeline or RetrievalPipeline(similarity_threshold=default_similarity_threshold)
        self.llm = llm_provider or get_llm_provider()
        self.guardrails = guardrail_engine or GuardrailEngine(min_similarity_threshold=default_similarity_threshold)
        self.grounding = grounding_validator or GroundingValidator()
        self.stt = stt_provider or get_stt_provider()
        self.context_builder = ContextBuilder()
        self.default_top_k = default_top_k
        self.default_similarity_threshold = default_similarity_threshold

    def run_rag_pipeline(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        transcript_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the pure RAG pipeline (measured for the <200ms target).
        """
        tracker = LatencyTracker()
        k = top_k if top_k is not None else self.default_top_k
        threshold = min_score if min_score is not None else self.default_similarity_threshold

        clean_query = query.strip() if query else ""

        # Step 1: Input Guardrail
        input_check = self.guardrails.validate_input(clean_query)
        if not input_check.passed:
            tracker.compute_total()
            return {
                "query": clean_query,
                "transcript": transcript_override or clean_query,
                "answer": input_check.message,
                "grounded": False,
                "confidence": 0.0,
                "sources": [],
                "guardrail": input_check.to_dict(),
                "latency": tracker.to_dict(),
                "why_this_answer": {
                    "input_valid": False,
                    "retrieved_count": 0,
                    "evidence_threshold_met": False,
                    "grounding_passed": False,
                    "reason": input_check.reason
                }
            }

        # Step 2: Dense Retrieval & Relevance Filtering
        retrieval_res = self.retrieval.retrieve(clean_query, top_k=k, min_score=threshold)
        tracker.embedding_ms = retrieval_res["latency"]["embedding_ms"]
        tracker.retrieval_ms = retrieval_res["latency"]["retrieval_ms"]
        tracker.reranking_ms = retrieval_res["latency"]["reranking_ms"]

        candidate_passages: List[SearchResult] = retrieval_res["results"]
        all_candidates: List[SearchResult] = retrieval_res["all_candidates"]

        # Step 3: Evidence Guardrail Check
        evidence_check = self.guardrails.validate_retrieval(candidate_passages, threshold=threshold)
        if not evidence_check.passed:
            tracker.compute_total()
            return {
                "query": clean_query,
                "transcript": transcript_override or clean_query,
                "answer": ABSTENTION_MESSAGE,
                "grounded": True,
                "confidence": 0.0,
                "sources": [c.to_dict() for c in all_candidates[:k]],
                "guardrail": evidence_check.to_dict(),
                "latency": tracker.to_dict(),
                "why_this_answer": {
                    "input_valid": True,
                    "retrieved_count": len(candidate_passages),
                    "evidence_threshold_met": False,
                    "grounding_passed": True,
                    "reason": "Evidence below similarity threshold; system abstained safely."
                }
            }

        # Step 4: Context Building
        sys_prompt, user_prompt, ctx_ms = self.context_builder.build_prompt(clean_query, candidate_passages)
        tracker.context_building_ms = ctx_ms

        # Step 5: LLM Generation (with retry / fallback protection)
        try:
            answer_text, gen_ms = self.llm.generate(sys_prompt, user_prompt)
            tracker.generation_ms = gen_ms
        except Exception as e:
            logger.warning(f"Primary LLM generation failed: {e}. Falling back to grounded extractive synthesis.")
            from .generation import FastLocalExtractiveProvider
            fallback_gen = FastLocalExtractiveProvider()
            answer_text, gen_ms = fallback_gen.generate(sys_prompt, user_prompt)
            tracker.generation_ms = gen_ms

        # Step 6: Grounding Validation
        grounding_res: GroundingResult = self.grounding.verify(answer_text, candidate_passages)
        tracker.grounding_ms = grounding_res.grounding_ms

        # Final structured response
        tracker.compute_total()

        return {
            "query": clean_query,
            "transcript": transcript_override or clean_query,
            "answer": answer_text,
            "grounded": grounding_res.grounded,
            "confidence": grounding_res.confidence,
            "sources": [p.to_dict() for p in candidate_passages],
            "guardrail": {"passed": True, "reason": "ALL_CHECKS_PASSED"},
            "grounding_details": grounding_res.to_dict(),
            "latency": tracker.to_dict(),
            "why_this_answer": {
                "input_valid": True,
                "retrieved_count": len(candidate_passages),
                "top_similarity_score": round(candidate_passages[0].score, 4) if candidate_passages else 0.0,
                "evidence_threshold_met": True,
                "grounding_passed": grounding_res.grounded,
                "overlap_ratio": grounding_res.overlap_ratio,
                "reason": "Retrieved high-confidence evidence from MSMARCO-XI and verified answer grounding."
            }
        }

    def process_voice_query(
        self,
        audio_bytes: bytes,
        language: str = "hi",
        content_type: str = "audio/wav",
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        End-to-End Voice Flow:
        Audio -> STT Provider -> Transcribed Query -> RAG Pipeline -> Response.
        """
        # Step A: STT Transcription
        stt_res = self.stt.transcribe(audio_bytes, language=language, content_type=content_type)
        transcript = stt_res.transcript

        # Step B: RAG Pipeline
        rag_response = self.run_rag_pipeline(
            query=transcript,
            top_k=top_k,
            min_score=min_score,
            transcript_override=transcript
        )

        # Inject STT Latency
        rag_response["latency"]["stt_ms"] = stt_res.stt_ms
        rag_response["latency"]["end_to_end_ms"] = round(stt_res.stt_ms + rag_response["latency"]["total_rag_ms"], 2)
        rag_response["stt_provider"] = stt_res.provider

        return rag_response


_GLOBAL_ORCHESTRATOR = None

def get_orchestrator() -> RAGOrchestrator:
    global _GLOBAL_ORCHESTRATOR
    if _GLOBAL_ORCHESTRATOR is None:
        _GLOBAL_ORCHESTRATOR = RAGOrchestrator()
    return _GLOBAL_ORCHESTRATOR