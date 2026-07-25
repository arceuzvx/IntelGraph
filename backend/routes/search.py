"""
IntelGraph — API routes.

Defines endpoints for search, related techniques, and filter metadata.
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from actian_vectorai import VectorAIError

log = logging.getLogger(__name__)

from models import (
    FiltersResponse,
    RelatedRequest,
    RelatedResponse,
    SearchRequest,
    SearchResponse,
)
from services import (
    find_related_techniques,
    get_available_filters,
    semantic_search,
)

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest, http_request: Request) -> SearchResponse:
    """Perform a semantic search with optional filters.

    Accepts a natural-language query and returns the most similar
    ATT&CK techniques from the IntelGraph collection.
    """
    try:
        results = semantic_search(
            query=request.query,
            client=http_request.app.state.vectorai_client,
            limit=request.limit,
            platform=request.platform,
            tactic=request.tactic,
        )
    except VectorAIError as exc:
        log.error("VectorAI search error: %s", exc.message)
        raise HTTPException(
            status_code=503,
            detail="VectorAI database service is currently unavailable.",
        ) from exc

    return SearchResponse(
        query=request.query,
        result_count=len(results),
        results=results,
    )


@router.post("/related", response_model=RelatedResponse)
def related(request: RelatedRequest, http_request: Request) -> RelatedResponse:
    """Find techniques semantically related to a given point."""
    try:
        source_title, items = find_related_techniques(
            point_id=request.point_id,
            client=http_request.app.state.vectorai_client,
            limit=request.limit,
        )
    except VectorAIError as exc:
        log.error("VectorAI related search error: %s", exc.message)
        raise HTTPException(
            status_code=503,
            detail="VectorAI database service is currently unavailable.",
        ) from exc

    return RelatedResponse(
        source_id=request.point_id,
        source_title=source_title,
        related=items,
    )


@router.get("/filters", response_model=FiltersResponse)
def filters() -> FiltersResponse:
    """Return available platform and tactic filter values."""
    data = get_available_filters()
    return FiltersResponse(
        platforms=data.get("platforms", []),
        tactics=data.get("tactics", []),
    )
