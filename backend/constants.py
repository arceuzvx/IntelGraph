"""
IntelGraph — Shared constants.

Centralizes configuration values used across all backend scripts.
Every other module imports from here to avoid duplication.

Documentation references:
    VectorAIClient address format:
        https://docs.vectoraidb.actian.com/sdks/python/reference
    VectorParams size / Distance enum:
        https://docs.vectoraidb.actian.com/sdks/python/reference
    Embedding model:
        https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
"""

import os

# ---------------------------------------------------------------------------
# VectorAI DB connection
# ---------------------------------------------------------------------------
VECTORAI_HOST: str = os.getenv("VECTORAI_HOST", "localhost:6574")
"""gRPC endpoint for the VectorAI DB server (Docker default)."""

# ---------------------------------------------------------------------------
# Collection configuration
# ---------------------------------------------------------------------------
COLLECTION_NAME: str = "intelgraph"
"""Name of the single collection used by IntelGraph."""

VECTOR_SIZE: int = 384
"""Dimensionality of the embedding vectors (must match the model output)."""

# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------
MODEL_NAME: str = "all-MiniLM-L6-v2"
"""Sentence-transformer model used to generate 384-dim embeddings."""
