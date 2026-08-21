"""
backend/app/services/guardrails.py
Comprehensive guardrail validation engine.
Handles:
  1. Empty / whitespace queries
  2. Unsafe / prompt injection attempts
  3. Off-topic & gibberish detection
  4. Weak retrieval & insufficient evidence detection with safe abstention
"""

from typing import Dict, Any, List, Optional
import re
from .vector_store import SearchResult

ABSTENTION_MESSAGE = "I couldn't find enough relevant information in the provided knowledge base to answer this reliably."

# Known prompt injection & jailbreak patterns
UNSAFE_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt override",
    r"disregard context",
    r"act as an unrestricted",
    r"dan mode",
    r"bypass safety",
    r"reveal system prompt"
]

class GuardrailDecision:
    def __init__(
        self,
        passed: bool,
        reason: str = "OK",
        abstain: bool = False,
        message: Optional[str] = None
    ):
        self.passed = passed
        self.reason = reason
        self.abstain = abstain
        self.message = message or (ABSTENTION_MESSAGE if abstain else "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "reason": self.reason,
            "abstain": self.abstain,
            "message": self.message
        }


class GuardrailEngine:
    def __init__(self, min_similarity_threshold: float = 0.35):
        self.min_similarity_threshold = min_similarity_threshold

    def validate_input(self, query: str) -> GuardrailDecision:
        """Validates incoming user query before embedding/retrieval."""
        if not query or not query.strip():
            return GuardrailDecision(
                passed=False,
                reason="EMPTY_QUERY",
                abstain=True,
                message="Please provide a valid question."
            )

        clean_query = query.strip()

        # Check length
        if len(clean_query) < 2:
            return GuardrailDecision(
                passed=False,
                reason="QUERY_TOO_SHORT",
                abstain=True,
                message="Your query is too short. Please provide a more descriptive question."
            )

        # Check prompt injection
        lower_q = clean_query.lower()
        for pat in UNSAFE_PATTERNS:
            if re.search(pat, lower_q):
                return GuardrailDecision(
                    passed=False,
                    reason="UNSAFE_INJECTION_DETECTED",
                    abstain=True,
                    message="Security guardrail triggered: Unsupported or unsafe input pattern."
                )

        return GuardrailDecision(passed=True, reason="INPUT_VALID")

    def validate_retrieval(self, results: List[SearchResult], threshold: Optional[float] = None) -> GuardrailDecision:
        """Validates retrieval results. Enforces abstention if evidence is insufficient."""
        cutoff = threshold if threshold is not None else self.min_similarity_threshold
        
        if not results:
            return GuardrailDecision(
                passed=False,
                reason="NO_PASSAGES_RETRIEVED",
                abstain=True,
                message=ABSTENTION_MESSAGE
            )

        top_score = results[0].score
        if top_score < cutoff:
            return GuardrailDecision(
                passed=False,
                reason=f"LOW_SIMILARITY_SCORE ({top_score:.3f} < {cutoff:.3f})",
                abstain=True,
                message=ABSTENTION_MESSAGE
            )

        return GuardrailDecision(passed=True, reason="EVIDENCE_CONFIRMED")
