"""
IntelGraph — Pydantic models for API request/response schemas.

Defines typed request and response models used by FastAPI routes.
Supports the enhanced MITRE ATT&CK payload format with optional
platform/tactic filters and related techniques.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    """Incoming search request body with optional metadata filters."""

    query: str = Field(..., min_length=1, description="Natural-language search query")
    limit: int = Field(default=5, ge=1, le=100, description="Max results to return")
    platform: Optional[str] = Field(default=None, description="Filter by platform")
    tactic: Optional[str] = Field(default=None, description="Filter by MITRE tactic")


class SearchResultItem(BaseModel):
    """A single search result with full ATT&CK metadata."""

    id: int
    score: float
    technique_id: str = ""
    title: str = ""
    description: str = ""
    platforms: List[str] = []
    tactics: List[str] = []
    data_sources: List[str] = []
    url: str = ""


class SearchResponse(BaseModel):
    """Response body for POST /api/search."""

    query: str
    result_count: int
    results: List[SearchResultItem]


# ---------------------------------------------------------------------------
# Related techniques
# ---------------------------------------------------------------------------

class RelatedRequest(BaseModel):
    """Request body for finding related techniques."""

    point_id: int = Field(..., description="ID of the source point")
    limit: int = Field(default=5, ge=1, le=20, description="Max related results")


class RelatedResponse(BaseModel):
    """Response body for POST /api/related."""

    source_id: int
    source_title: str
    related: List[SearchResultItem]


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

class FiltersResponse(BaseModel):
    """Available filter values for the frontend dropdowns."""

    platforms: List[str]
    tactics: List[str]
