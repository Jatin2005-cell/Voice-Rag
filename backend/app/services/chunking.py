"""
backend/app/services/chunking.py
Multi-strategy chunking engine for MSMARCO-XI and multilingual RAG pipelines.
Supports:
  1. Passage-Aware (Preserves natural dataset passage boundaries, chunks oversized passages)
  2. Fixed-Size (Fixed word/character chunks)
  3. Overlapping (Sliding window with overlap)
  4. Metadata-Aware (Prepends semantic headers & category context)
"""

from typing import List, Dict, Any, Optional
import uuid
import re

class ChunkRecord:
    def __init__(
        self,
        chunk_id: str,
        query_id: int,
        passage_idx: int,
        chunk_idx: int,
        text: str,
        english_text: str,
        language: str,
        source_lang: str,
        target_lang: str,
        is_selected: int,
        strategy: str,
        query_type: Optional[str] = None,
        word_count: int = 0,
        char_count: int = 0
    ):
        self.chunk_id = chunk_id
        self.query_id = query_id
        self.passage_idx = passage_idx
        self.chunk_idx = chunk_idx
        self.text = text
        self.english_text = english_text
        self.language = language
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.is_selected = is_selected
        self.strategy = strategy
        self.query_type = query_type
        self.word_count = word_count or len(text.split())
        self.char_count = char_count or len(text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "query_id": self.query_id,
            "passage_idx": self.passage_idx,
            "chunk_idx": self.chunk_idx,
            "text": self.text,
            "english_text": self.english_text,
            "language": self.language,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "is_selected": self.is_selected,
            "strategy": self.strategy,
            "query_type": self.query_type,
            "word_count": self.word_count,
            "char_count": self.char_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChunkRecord':
        return cls(**data)


class BaseChunker:
    def chunk_record(self, raw_record: Dict[str, Any]) -> List[ChunkRecord]:
        raise NotImplementedError


class PassageAwareChunker(BaseChunker):
    """
    Primary chunking strategy. Respects MSMARCO natural passage boundaries.
    Only splits when a passage exceeds max_words (e.g. 250 words).
    """
    def __init__(self, max_words: int = 250, sub_chunk_overlap: int = 30):
        self.max_words = max_words
        self.sub_chunk_overlap = sub_chunk_overlap

    def chunk_record(self, raw_record: Dict[str, Any]) -> List[ChunkRecord]:
        chunks = []
        query_id = raw_record.get("query_id")
        query_type = raw_record.get("query_type")
        target_lang = raw_record.get("target_lang", "hi")
        source_lang = raw_record.get("source_lang", "en")
        passages = raw_record.get("passages", {})
        
        trans_passages = passages.get("Translated_passages", [])
        eng_passages = passages.get("English_passages", [])
        is_selected = passages.get("is_selected", [])

        for p_idx, text in enumerate(trans_passages):
            eng_text = eng_passages[p_idx] if p_idx < len(eng_passages) else ""
            selected_flag = is_selected[p_idx] if p_idx < len(is_selected) else 0
            
            if not text or not text.strip():
                continue

            words = text.split()
            if len(words) <= self.max_words:
                chunk_id = f"q{query_id}_p{p_idx}_c0"
                chunks.append(ChunkRecord(
                    chunk_id=chunk_id,
                    query_id=query_id,
                    passage_idx=p_idx,
                    chunk_idx=0,
                    text=text.strip(),
                    english_text=eng_text.strip(),
                    language=target_lang,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    is_selected=selected_flag,
                    strategy="passage_aware",
                    query_type=query_type,
                    word_count=len(words),
                    char_count=len(text)
                ))
            else:
                # Sub-chunk oversized passage
                start = 0
                sub_c_idx = 0
                step = max(1, self.max_words - self.sub_chunk_overlap)
                while start < len(words):
                    sub_words = words[start:start + self.max_words]
                    sub_text = " ".join(sub_words)
                    chunk_id = f"q{query_id}_p{p_idx}_c{sub_c_idx}"
                    chunks.append(ChunkRecord(
                        chunk_id=chunk_id,
                        query_id=query_id,
                        passage_idx=p_idx,
                        chunk_idx=sub_c_idx,
                        text=sub_text,
                        english_text=eng_text.strip(),
                        language=target_lang,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        is_selected=selected_flag,
                        strategy="passage_aware",
                        query_type=query_type,
                        word_count=len(sub_words),
                        char_count=len(sub_text)
                    ))
                    start += step
                    sub_c_idx += 1

        return chunks


class FixedSizeChunker(BaseChunker):
    """
    Fixed word-length chunking.
    """
    def __init__(self, chunk_words: int = 150):
        self.chunk_words = chunk_words

    def chunk_record(self, raw_record: Dict[str, Any]) -> List[ChunkRecord]:
        chunks = []
        query_id = raw_record.get("query_id")
        query_type = raw_record.get("query_type")
        target_lang = raw_record.get("target_lang", "hi")
        source_lang = raw_record.get("source_lang", "en")
        passages = raw_record.get("passages", {})
        
        trans_passages = passages.get("Translated_passages", [])
        eng_passages = passages.get("English_passages", [])
        is_selected = passages.get("is_selected", [])

        for p_idx, text in enumerate(trans_passages):
            eng_text = eng_passages[p_idx] if p_idx < len(eng_passages) else ""
            selected_flag = is_selected[p_idx] if p_idx < len(is_selected) else 0
            
            if not text or not text.strip():
                continue

            words = text.split()
            for c_idx, i in enumerate(range(0, len(words), self.chunk_words)):
                sub_words = words[i:i + self.chunk_words]
                sub_text = " ".join(sub_words)
                chunk_id = f"q{query_id}_p{p_idx}_fc{c_idx}"
                chunks.append(ChunkRecord(
                    chunk_id=chunk_id,
                    query_id=query_id,
                    passage_idx=p_idx,
                    chunk_idx=c_idx,
                    text=sub_text,
                    english_text=eng_text.strip(),
                    language=target_lang,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    is_selected=selected_flag,
                    strategy="fixed_size",
                    query_type=query_type,
                    word_count=len(sub_words),
                    char_count=len(sub_text)
                ))
        return chunks


class OverlappingChunker(BaseChunker):
    """
    Sliding window chunking with configurable overlap.
    """
    def __init__(self, chunk_words: int = 150, overlap_words: int = 50):
        self.chunk_words = chunk_words
        self.overlap_words = overlap_words

    def chunk_record(self, raw_record: Dict[str, Any]) -> List[ChunkRecord]:
        chunks = []
        query_id = raw_record.get("query_id")
        query_type = raw_record.get("query_type")
        target_lang = raw_record.get("target_lang", "hi")
        source_lang = raw_record.get("source_lang", "en")
        passages = raw_record.get("passages", {})
        
        trans_passages = passages.get("Translated_passages", [])
        eng_passages = passages.get("English_passages", [])
        is_selected = passages.get("is_selected", [])

        step = max(1, self.chunk_words - self.overlap_words)
        for p_idx, text in enumerate(trans_passages):
            eng_text = eng_passages[p_idx] if p_idx < len(eng_passages) else ""
            selected_flag = is_selected[p_idx] if p_idx < len(is_selected) else 0
            
            if not text or not text.strip():
                continue

            words = text.split()
            start = 0
            c_idx = 0
            while start < len(words):
                sub_words = words[start:start + self.chunk_words]
                sub_text = " ".join(sub_words)
                chunk_id = f"q{query_id}_p{p_idx}_oc{c_idx}"
                chunks.append(ChunkRecord(
                    chunk_id=chunk_id,
                    query_id=query_id,
                    passage_idx=p_idx,
                    chunk_idx=c_idx,
                    text=sub_text,
                    english_text=eng_text.strip(),
                    language=target_lang,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    is_selected=selected_flag,
                    strategy="overlapping",
                    query_type=query_type,
                    word_count=len(sub_words),
                    char_count=len(sub_text)
                ))
                start += step
                c_idx += 1
        return chunks


class MetadataAwareChunker(BaseChunker):
    """
    Enriches chunks with contextual metadata prefixes (query_type, topic context).
    """
    def __init__(self, base_chunker: Optional[BaseChunker] = None):
        self.base_chunker = base_chunker or PassageAwareChunker()

    def chunk_record(self, raw_record: Dict[str, Any]) -> List[ChunkRecord]:
        base_chunks = self.base_chunker.chunk_record(raw_record)
        query_type = raw_record.get("query_type", "GENERAL")
        for chunk in base_chunks:
            chunk.text = f"[{query_type}] {chunk.text}"
            chunk.strategy = "metadata_aware"
        return base_chunks


def get_chunker(strategy: str = "passage") -> BaseChunker:
    strategy = (strategy or "passage").lower()
    if strategy in ("passage", "passage_aware", "semantic"):
        return PassageAwareChunker()
    elif strategy in ("fixed", "fixed_size"):
        return FixedSizeChunker()
    elif strategy in ("overlap", "overlapping"):
        return OverlappingChunker()
    elif strategy in ("metadata", "metadata_aware"):
        return MetadataAwareChunker()
    else:
        return PassageAwareChunker()
