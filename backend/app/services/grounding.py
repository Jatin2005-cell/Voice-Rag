"""
backend/app/services/grounding.py
Grounding verification and hallucination detection service.
Verifies that generated responses are strictly anchored in retrieved context.
"""

from typing import List, Dict, Any, Tuple
import re
import time
from .vector_store import SearchResult

class GroundingResult:
    def __init__(
        self,
        grounded: bool,
        confidence: float,
        overlap_ratio: float,
        supported_claims: List[str],
        unsupported_claims: List[str],
        grounding_ms: float = 0.0
    ):
        self.grounded = grounded
        self.confidence = round(confidence, 4)
        self.overlap_ratio = round(overlap_ratio, 4)
        self.supported_claims = supported_claims
        self.unsupported_claims = unsupported_claims
        self.grounding_ms = round(grounding_ms, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grounded": self.grounded,
            "confidence": self.confidence,
            "overlap_ratio": self.overlap_ratio,
            "supported_claims": self.supported_claims,
            "unsupported_claims": self.unsupported_claims,
            "grounding_ms": self.grounding_ms
        }


class GroundingValidator:
    def __init__(self, min_grounding_threshold: float = 0.35):
        self.min_grounding_threshold = min_grounding_threshold

    def verify(self, answer: str, context_passages: List[SearchResult]) -> GroundingResult:
        t0 = time.perf_counter()

        if not answer or not answer.strip():
            ms = (time.perf_counter() - t0) * 1000.0
            return GroundingResult(
                grounded=False,
                confidence=0.0,
                overlap_ratio=0.0,
                supported_claims=[],
                unsupported_claims=["Empty answer"],
                grounding_ms=ms
            )

        # If answer is an abstention message, it is correctly grounded in the abstention guardrail
        if "couldn't find enough relevant information" in answer or "पर्याप्त जानकारी नहीं" in answer:
            ms = (time.perf_counter() - t0) * 1000.0
            return GroundingResult(
                grounded=True,
                confidence=1.0,
                overlap_ratio=1.0,
                supported_claims=["System abstention triggered on insufficient context"],
                unsupported_claims=[],
                grounding_ms=ms
            )

        if not context_passages:
            ms = (time.perf_counter() - t0) * 1000.0
            return GroundingResult(
                grounded=False,
                confidence=0.0,
                overlap_ratio=0.0,
                supported_claims=[],
                unsupported_claims=["No supporting passages available"],
                grounding_ms=ms
            )

        # Aggregate context tokens
        context_text = " ".join([p.text for p in context_passages]).lower()
        context_tokens = set(re.findall(r"\w+", context_text))

        # Split answer into sentences / claim units
        raw_sentences = [s.strip() for s in re.split(r"[।\.\n\?]+", answer) if len(s.strip()) > 3]
        if not raw_sentences:
            raw_sentences = [answer.strip()]

        supported = []
        unsupported = []
        sentence_overlaps = []

        for sent in raw_sentences:
            sent_tokens = set(re.findall(r"\w+", sent.lower()))
            # Remove very short stop-like tokens
            filtered_tokens = {t for t in sent_tokens if len(t) > 1}
            if not filtered_tokens:
                continue

            overlap = len(filtered_tokens.intersection(context_tokens)) / len(filtered_tokens)
            sentence_overlaps.append(overlap)

            if overlap >= self.min_grounding_threshold:
                supported.append(sent)
            else:
                unsupported.append(sent)

        avg_overlap = sum(sentence_overlaps) / max(1, len(sentence_overlaps))
        
        # Base confidence calculation combining highest passage score and token overlap
        top_passage_score = context_passages[0].score if context_passages else 0.5
        confidence = min(1.0, (avg_overlap * 0.5) + (top_passage_score * 0.5))

        is_grounded = (avg_overlap >= self.min_grounding_threshold) and (len(unsupported) <= len(supported))
        
        ms = (time.perf_counter() - t0) * 1000.0
        return GroundingResult(
            grounded=is_grounded,
            confidence=confidence,
            overlap_ratio=avg_overlap,
            supported_claims=supported,
            unsupported_claims=unsupported,
            grounding_ms=ms
        )
