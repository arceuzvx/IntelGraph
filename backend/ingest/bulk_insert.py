"""
IntelGraph — Bulk vector insertion.

Embeds parsed MITRE ATT&CK techniques and inserts them into VectorAI
in batches, using the existing singleton embedding model.
"""

import logging
import math
from typing import List

from actian_vectorai import PointStruct, VectorAIClient

from constants import COLLECTION_NAME, VECTORAI_HOST
from embed import embed_batch
from ingest.parser import MitreTechnique

log = logging.getLogger(__name__)

BATCH_SIZE: int = 200


def _build_payload(technique: MitreTechnique) -> dict:
    """Build the VectorAI payload dict for a technique."""
    return {
        "type": "attack-technique",
        "technique_id": technique.technique_id,
        "title": technique.name,
        "description": technique.description,
        "platforms": technique.platforms,
        "tactics": technique.tactics,
        "data_sources": technique.data_sources,
        "detection": technique.detection,
        "url": technique.url,
        
        # Backward compatibility for search_demo.py and smoke_test.py
        "platform": ", ".join(technique.platforms) if technique.platforms else "N/A",
        "tactic": ", ".join(technique.tactics) if technique.tactics else "N/A",
    }


def _build_embed_text(technique: MitreTechnique) -> str:
    """Combine relevant fields into a single string for embedding.

    Concatenating the name, description, tactics, and platforms
    produces richer semantic vectors than description alone.
    """
    parts = [
        technique.name,
        technique.description,
        " ".join(technique.tactics),
        " ".join(technique.platforms),
    ]
    return " ".join(parts)


def bulk_insert_techniques(techniques: List[MitreTechnique]) -> int:
    """Embed and insert techniques into VectorAI in batches.

    Args:
        techniques: Parsed MitreTechnique objects.

    Returns:
        Total number of points inserted.
    """
    total = len(techniques)
    num_batches = math.ceil(total / BATCH_SIZE)
    inserted = 0

    log.info("Inserting %d techniques in %d batches (size=%d) ...", total, num_batches, BATCH_SIZE)

    with VectorAIClient(VECTORAI_HOST) as client:
        for batch_idx in range(num_batches):
            start = batch_idx * BATCH_SIZE
            end = min(start + BATCH_SIZE, total)
            batch = techniques[start:end]

            # Embed all descriptions in a single forward pass
            texts = [_build_embed_text(t) for t in batch]
            log.info(
                "Embedding batch %d/%d (%d texts) ...",
                batch_idx + 1, num_batches, len(texts),
            )
            vectors = embed_batch(texts)

            # Build PointStruct objects
            points = [
                PointStruct(
                    id=technique.point_id,
                    vector=vector,
                    payload=_build_payload(technique),
                )
                for technique, vector in zip(batch, vectors)
            ]

            # Upsert the batch
            client.points.upsert(COLLECTION_NAME, points)
            inserted += len(points)
            log.info("Inserted %d/%d vectors.", inserted, total)

    return inserted
