"""
IntelGraph — Embedding helper.

Loads the sentence-transformer model exactly once at module-import time
and exposes a single function for the rest of the codebase.

Documentation references:
    Model:       https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    SDK usage:   https://docs.vectoraidb.actian.com/academy/tutorials/first-application
                 (Step 5 — "Create embedding helpers")
"""

from typing import List

from sentence_transformers import SentenceTransformer

from constants import MODEL_NAME

# ---------------------------------------------------------------------------
# Singleton model instance — loaded once when this module is first imported.
# ---------------------------------------------------------------------------
_model: SentenceTransformer = SentenceTransformer(MODEL_NAME)


def embed(text: str) -> List[float]:
    """Convert a single text string to a 384-dimensional vector.

    Args:
        text: The input text to embed.

    Returns:
        A list of floats representing the embedding vector.

    Documentation reference:
        https://docs.vectoraidb.actian.com/academy/tutorials/first-application
        (Step 5 — embed_text helper)
    """
    return _model.encode(text).tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Convert a batch of text strings to vectors in a single forward pass.

    Significantly faster than calling embed() in a loop.

    Args:
        texts: List of input texts to embed.

    Returns:
        A list of embedding vectors.
    """
    return _model.encode(texts).tolist()