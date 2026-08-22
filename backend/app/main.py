"""
backend/app/main.py
FastAPI application entrypoint for VoiceRAG.
Ask. Retrieve. Verify.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from .config import settings
from .api import health, query, voice, evaluation, system
from .services.vector_store import get_vector_store
from .services.embeddings import preload_embedding_provider
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"Voice-Enabled RAG System: {settings.TAGLINE}",
    version=settings.VERSION
)

# Configure CORS for both local development and production deployments
origins = [o.strip() for o in settings.FRONTEND_ORIGIN.split(",") if o.strip()]
if "*" in origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(voice.router, prefix="/api", tags=["Voice"])
app.include_router(evaluation.router, prefix="/api", tags=["Evaluation"])
app.include_router(system.router, prefix="/api", tags=["System"])

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing VoiceRAG application services...")

    # ---------------------------------------------------------
    # 1. Preload embedding model ONCE
    # ---------------------------------------------------------
    try:
        embedder = preload_embedding_provider()

        logger.info(
            f"Embedding model loaded: "
            f"{embedder.model_name}"
        )

        logger.info(
            f"Embedding dimension: "
            f"{embedder.dimension}"
        )

    except Exception as e:
        logger.exception(
            f"Failed to preload embedding model: {e}"
        )
        raise

    # ---------------------------------------------------------
    # 2. Preload vector index ONCE
    # ---------------------------------------------------------
    try:
        store = get_vector_store()

        logger.info(
            f"Vector Store initialized with "
            f"{store.count()} chunks."
        )

    except Exception as e:
        logger.warning(
            f"Vector store not yet indexed: {e}"
        )

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "status": "online",
        "docs_url": "/docs"
    }
