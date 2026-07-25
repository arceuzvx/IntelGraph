"""
IntelGraph — Search service.

Enhanced semantic search with optional metadata filtering,
related-technique discovery, and backward-compatible payload handling.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from actian_vectorai import (
    Field as VField,
    FilterBuilder,
    VectorAIClient,
    VectorAIError,
)

from constants import COLLECTION_NAME
from embed import embed
from models import SearchResultItem

log = logging.getLogger(__name__)

FILTERS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "filters.json"


def _payload_to_result(point_id: int, score: float, payload: dict) -> SearchResultItem:
    """Map a VectorAI payload to a SearchResultItem.

    Handles both old-format payloads (platform/tactic as strings)
    and new-format payloads (platforms/tactics as lists).
    """
    # Backward compat: wrap scalar platform/tactic into lists
    platforms = payload.get("platforms", [])
    if not platforms and "platform" in payload:
        platforms = [payload["platform"]]

    tactics = payload.get("tactics", [])
    if not tactics and "tactic" in payload:
        tactics = [payload["tactic"]]

    return SearchResultItem(
        id=point_id,
        score=round(score, 4),
        technique_id=payload.get("technique_id", ""),
        title=payload.get("title", "N/A"),
        description=payload.get("description", "N/A"),
        platforms=platforms,
        tactics=tactics,
        data_sources=payload.get("data_sources", []),
        url=payload.get("url", ""),
    )


def semantic_search(
    query: str,
    client: VectorAIClient,
    limit: int = 5,
    platform: Optional[str] = None,
    tactic: Optional[str] = None,
) -> List[SearchResultItem]:
    """Perform a semantic search with optional metadata filters.

    Args:
        query:    Natural-language search string.
        limit:    Maximum number of results.
        platform: Optional platform filter (e.g. "Windows").
        tactic:   Optional tactic filter (e.g. "Credential Access").

    Returns:
        A list of SearchResultItem objects ordered by descending score.
    """
    query_vector = embed(query)

    # Build optional filter
    search_filter = None
    if platform or tactic:
        builder = FilterBuilder()
        if platform:
            builder = builder.must(VField("platforms").text(platform))
        if tactic:
            builder = builder.must(VField("tactics").text(tactic))
        search_filter = builder.build()

    kwargs = {
        "vector": query_vector,
        "limit": limit,
        "with_payload": True,
    }
    if search_filter is not None:
        kwargs["filter"] = search_filter

    results = client.points.search(COLLECTION_NAME, **kwargs)

    if not results:
        return []

    return [
        _payload_to_result(r.id, r.score, r.payload or {})
        for r in results
    ]


def find_related_techniques(
    point_id: int,
    client: VectorAIClient,
    limit: int = 5,
) -> tuple:
    """Find techniques semantically similar to the given point.

    Retrieves the source point's vector and searches for neighbours,
    excluding the source point itself.

    Args:
        point_id: The VectorAI point ID.
        limit:    Max number of related results.

    Returns:
        Tuple of (source_title, list_of_SearchResultItem).
    """
    # Retrieve the source point with its vector
    points = client.points.get(
        COLLECTION_NAME,
        ids=[point_id],
        with_payload=True,
        with_vectors=True,
    )

    if not points:
        return ("Unknown", [])

    source = points[0]
    source_payload = source.payload or {}
    source_title = source_payload.get("title", "Unknown")
    source_vector = source.vectors

    if not source_vector:
        return (source_title, [])

    # Search for similar vectors, requesting one extra to drop self
    results = client.points.search(
        COLLECTION_NAME,
        vector=source_vector,
        limit=limit + 1,
        with_payload=True,
    )

    # Filter out the source point itself
    related = [
        _payload_to_result(r.id, r.score, r.payload or {})
        for r in results
        if r.id != point_id
    ][:limit]

    return (source_title, related)


def get_available_filters() -> dict:
    """Load the platform/tactic filter metadata generated during ingestion.

    Returns:
        Dict with 'platforms' and 'tactics' lists, or empty lists if
        the metadata file does not exist yet.
    """
    if not FILTERS_PATH.exists():
        return {"platforms": [], "tactics": []}
    with open(FILTERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
