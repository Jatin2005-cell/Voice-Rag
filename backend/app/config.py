"""
backend/app/config.py
Application configuration and environment management.
"""

import os

class Settings:
    PROJECT_NAME: str = "VoiceRAG"
    TAGLINE: str = "Ask. Retrieve. Verify."
    VERSION: str = "1.0.0"

    # Dataset settings
    DATASET_NAME: str = "ai4bharat/MSMARCO-XI"
    DATASET_LANGUAGE: str = os.getenv("DATASET_LANGUAGE", "hi")
    DATASET_SPLIT: str = os.getenv("DATASET_SPLIT", "validation")
    MAX_ROWS: int = int(os.getenv("MAX_ROWS", "200"))

    # Chunking & Retrieval
    CHUNKING_STRATEGY: str = os.getenv("CHUNKING_STRATEGY", "passage")
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))
    RERANKING_ENABLED: bool = os.getenv("RERANKING_ENABLED", "false").lower() in ("true", "1", "yes")

    # Embeddings & Store
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "mock")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    INDEX_DIR: str = os.getenv("INDEX_DIR", "data/index")

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # STT Provider
    STT_PROVIDER: str = os.getenv("STT_PROVIDER", "sarvam")
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")

    # Latency Target
    LATENCY_TARGET_MS: float = 200.0

    # CORS
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")

settings = Settings()