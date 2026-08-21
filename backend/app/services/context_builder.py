"""
backend/app/services/context_builder.py
Constructs structured context payloads and grounded prompts for LLM synthesis.
"""

from typing import List, Dict, Any, Tuple
import time
from .vector_store import SearchResult

SYSTEM_PROMPT = """You are VoiceRAG, an accurate, grounded, and concise AI assistant.
Answer the user's question ONLY using the provided evidence passages below.

STRICT GROUNDING RULES:
1. Base your answer strictly on the provided Passages.
2. If the passages do not contain enough information to answer the question with certainty, respond with:
"I couldn't find enough relevant information in the provided knowledge base to answer this reliably."
3. Do NOT guess or use outside knowledge.
4. Keep the answer concise (2-4 sentences), factual, and directly in the language of the question (Hindi or English).
"""

class ContextBuilder:
    def build_prompt(self, query: str, passages: List[SearchResult]) -> Tuple[str, str, float]:
        """
        Builds (system_prompt, user_prompt, context_building_ms).
        """
        t0 = time.perf_counter()

        formatted_passages = []
        for idx, p in enumerate(passages, start=1):
            formatted_passages.append(
                f"[Passage {idx}] (Score: {p.score:.3f}, ID: {p.chunk_id})\n{p.text.strip()}"
            )

        passages_block = "\n\n".join(formatted_passages)

        user_prompt = f"""EVIDENCE PASSAGES:
{passages_block}

USER QUESTION:
{query}

GROUNDED ANSWER:"""

        ms = (time.perf_counter() - t0) * 1000.0
        return SYSTEM_PROMPT, user_prompt, ms
