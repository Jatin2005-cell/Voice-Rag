"""
backend/app/services/embeddings.py

Multilingual embedding provider abstraction and implementations.
The embedding model is loaded ONCE during application startup
and reused for all subsequent queries.
"""

from typing import List, Optional
import numpy as np
import os
import hashlib
import threading


class EmbeddingProvider:
    """Abstract base class for all embedding providers."""

    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 64
    ) -> List[List[float]]:
        raise NotImplementedError

    def preload(self):
        """Load/warm the model before serving requests."""
        pass

    @property
    def dimension(self) -> int:
        raise NotImplementedError

    @property
    def model_name(self) -> str:
        raise NotImplementedError


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """
    Multilingual SentenceTransformers embedding provider.

    The model is loaded once and kept in memory for the lifetime
    of the application.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        device: Optional[str] = None
    ):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._dim = 384

        # Cache repeated query embeddings
        self._query_cache = {}

        # Prevent multiple simultaneous model loads
        self._load_lock = threading.Lock()

    def _load_model(self):
        """
        Load the embedding model exactly once.
        """
        if self._model is not None:
            return

        with self._load_lock:
            # Double check after acquiring lock
            if self._model is not None:
                return

            from sentence_transformers import SentenceTransformer
            import torch

            if not self._device:
                self._device = (
                    "cuda"
                    if torch.cuda.is_available()
                    else "cpu"
                )

            print(
                f"[Embedding] Loading model: {self._model_name}"
            )
            print(
                f"[Embedding] Device: {self._device}"
            )

            self._model = SentenceTransformer(
                self._model_name,
                device=self._device
            )

            if hasattr(
                self._model,
                "get_embedding_dimension"
            ):
                self._dim = self._model.get_embedding_dimension()

            elif hasattr(
                self._model,
                "get_sentence_embedding_dimension"
            ):
                self._dim = (
                    self._model
                    .get_sentence_embedding_dimension()
                )

            else:
                self._dim = 384

            print(
                f"[Embedding] Model loaded successfully. "
                f"Dimension: {self._dim}"
            )

    def preload(self):
        """
        Explicitly load the model during application startup.

        This moves the expensive model initialization away from
        the first user query.
        """
        self._load_model()

        # Warm-up inference.
        # This prevents first real query from paying framework/
        # tokenizer initialization overhead.
        try:
            self._model.encode(
                ["warmup"],
                normalize_embeddings=True,
                show_progress_bar=False
            )
            print("[Embedding] Warm-up completed.")
        except Exception as e:
            print(
                f"[Embedding] Warm-up warning: {e}"
            )

    @property
    def dimension(self) -> int:
        self._load_model()
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding using the already-loaded model.
        """

        text = (text or "").strip()

        if not text:
            return [0.0] * self._dim

        # Fast cache lookup
        cache_key = hashlib.md5(
            text.encode("utf-8")
        ).hexdigest()

        cached = self._query_cache.get(cache_key)

        if cached is not None:
            return cached

        # Model should already be loaded during startup.
        # This is only a safety fallback.
        self._load_model()

        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        emb_list = (
            embedding.tolist()
            if hasattr(embedding, "tolist")
            else list(embedding)
        )

        # Keep cache bounded
        if len(self._query_cache) >= 1000:
            self._query_cache.pop(
                next(iter(self._query_cache))
            )

        self._query_cache[cache_key] = emb_list

        return emb_list

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 64
    ) -> List[List[float]]:

        self._load_model()

        clean_texts = [
            t.strip() if t else ""
            for t in texts
        ]

        embeddings = self._model.encode(
            clean_texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return (
            embeddings.tolist()
            if hasattr(embeddings, "tolist")
            else [list(e) for e in embeddings]
        )


class FastHashMockEmbeddingProvider(EmbeddingProvider):
    """
    Ultra-lightweight deterministic embedding provider
    for test/mock pipelines.
    """

    def __init__(self, dimension: int = 384):
        self._dim = dimension
        self._model_name = (
            "fast-hash-mock-multilingual-384"
        )

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model_name

    def preload(self):
        pass

    def embed_text(self, text: str) -> List[float]:

        text_bytes = (
            text.strip()
            .encode("utf-8")
        )

        rng = np.random.RandomState(
            int(
                hashlib.sha256(
                    text_bytes
                ).hexdigest()[:8],
                16
            )
        )

        vec = rng.randn(
            self._dim
        ).astype(np.float32)

        norm = np.linalg.norm(vec)

        if norm > 0:
            vec /= norm

        return vec.tolist()

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 64
    ) -> List[List[float]]:

        return [
            self.embed_text(t)
            for t in texts
        ]


_GLOBAL_EMBEDDING_PROVIDER = None


def get_embedding_provider(
    provider_type: Optional[str] = None,
    model_name: Optional[str] = None
) -> EmbeddingProvider:

    global _GLOBAL_EMBEDDING_PROVIDER

    if _GLOBAL_EMBEDDING_PROVIDER is not None:
        return _GLOBAL_EMBEDDING_PROVIDER

    provider = (
        provider_type
        or os.getenv(
            "EMBEDDING_PROVIDER",
            "sentence_transformers"
        )
    ).lower()

    model = (
        model_name
        or os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        )
    )

    if provider in (
        "sentence_transformers",
        "st",
        "local",
        "multilingual"
    ):
        _GLOBAL_EMBEDDING_PROVIDER = (
            SentenceTransformerEmbeddingProvider(
                model_name=model
            )
        )

    elif provider in (
        "mock",
        "fast_test"
    ):
        _GLOBAL_EMBEDDING_PROVIDER = (
            FastHashMockEmbeddingProvider()
        )

    else:
        _GLOBAL_EMBEDDING_PROVIDER = (
            SentenceTransformerEmbeddingProvider(
                model_name=model
            )
        )

    return _GLOBAL_EMBEDDING_PROVIDER


def preload_embedding_provider():
    """
    Load and warm the global embedding provider.
    Called once during FastAPI startup.
    """

    provider = get_embedding_provider()
    provider.preload()

    return provider