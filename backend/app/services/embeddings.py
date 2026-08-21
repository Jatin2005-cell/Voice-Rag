"""
backend/app/services/embeddings.py
Multilingual embedding provider abstraction and implementations.
Optimized for Indic languages (Hindi, Bengali, Tamil, etc.) with precomputation and query embedding caching.
"""

from typing import List, Optional, Union
import numpy as np
import time
import os
import hashlib
from functools import lru_cache

class EmbeddingProvider:
    """Abstract base class for all embedding providers."""
    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        raise NotImplementedError

    @property
    def dimension(self) -> int:
        raise NotImplementedError

    @property
    def model_name(self) -> str:
        raise NotImplementedError


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """
    Multilingual SentenceTransformers embedding provider.
    Defaults to 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2' (384-dim, 50+ languages including Indic).
    Extremely fast CPU/GPU inference.
    """
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device: Optional[str] = None):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._dim = 384
        self._query_cache = {}  # In-memory fast cache for repeated query embeddings

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            import torch
            if not self._device:
                self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = SentenceTransformer(self._model_name, device=self._device)
            if hasattr(self._model, "get_embedding_dimension"):
                self._dim = self._model.get_embedding_dimension()
            elif hasattr(self._model, "get_sentence_embedding_dimension"):
                self._dim = self._model.get_sentence_embedding_dimension()
            else:
                self._dim = 384

    @property
    def dimension(self) -> int:
        self._load_model()
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_text(self, text: str) -> List[float]:
        text = text.strip()
        # Fast query cache lookup
        cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]

        self._load_model()
        embedding = self._model.encode(text, normalize_embeddings=True, show_progress_bar=False)
        emb_list = embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
        
        # Cache top 1000 query embeddings
        if len(self._query_cache) < 1000:
            self._query_cache[cache_key] = emb_list
            
        return emb_list

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        self._load_model()
        clean_texts = [t.strip() if t else "" for t in texts]
        embeddings = self._model.encode(
            clean_texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.tolist() if hasattr(embeddings, "tolist") else [list(e) for e in embeddings]


class FastHashMockEmbeddingProvider(EmbeddingProvider):
    """
    Ultra-lightweight deterministic embedding provider for instant test/mock pipelines.
    """
    def __init__(self, dimension: int = 384):
        self._dim = dimension
        self._model_name = "fast-hash-mock-multilingual-384"

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_text(self, text: str) -> List[float]:
        text_bytes = text.strip().encode('utf-8')
        rng = np.random.RandomState(int(hashlib.sha256(text_bytes).hexdigest()[:8], 16))
        vec = rng.randn(self._dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


_GLOBAL_EMBEDDING_PROVIDER = None

def get_embedding_provider(provider_type: Optional[str] = None, model_name: Optional[str] = None) -> EmbeddingProvider:
    global _GLOBAL_EMBEDDING_PROVIDER
    if _GLOBAL_EMBEDDING_PROVIDER is not None:
        return _GLOBAL_EMBEDDING_PROVIDER

    provider = (provider_type or os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")).lower()
    model = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    if provider in ("sentence_transformers", "st", "local", "multilingual"):
        _GLOBAL_EMBEDDING_PROVIDER = SentenceTransformerEmbeddingProvider(model_name=model)
    elif provider in ("mock", "fast_test"):
        _GLOBAL_EMBEDDING_PROVIDER = FastHashMockEmbeddingProvider()
    else:
        _GLOBAL_EMBEDDING_PROVIDER = SentenceTransformerEmbeddingProvider(model_name=model)

    return _GLOBAL_EMBEDDING_PROVIDER
