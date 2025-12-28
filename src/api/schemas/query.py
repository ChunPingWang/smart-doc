"""Query-related Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ResponseMode(str, Enum):
    """Response generation mode."""

    CONCISE = "concise"
    DETAILED = "detailed"
    COMPARISON = "comparison"


class QueryFilters(BaseModel):
    """Filters for query requests."""

    doc_types: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class SearchRequest(BaseModel):
    """Search request payload."""

    query: str = Field(..., min_length=1, description="Search query text")
    filters: Optional[QueryFilters] = None
    top_k: int = Field(default=5, ge=1, le=20)
    include_cross_reference: bool = True


class CrossReference(BaseModel):
    """Cross-referenced document information."""

    chunk_id: str
    document_id: str
    type: str
    table_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    relevance: str = "medium"


class SearchResult(BaseModel):
    """Single search result."""

    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict
    cross_references: list[CrossReference] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Search response payload."""

    results: list[SearchResult]
    query_time_ms: int


class QueryRequest(BaseModel):
    """Base query request."""

    query: str = Field(..., min_length=1)
    filters: Optional[QueryFilters] = None
    top_k: int = Field(default=5, ge=1, le=20)
    include_cross_reference: bool = True
    response_mode: ResponseMode = ResponseMode.CONCISE


class AskRequest(BaseModel):
    """Ask (QA) request payload."""

    question: str = Field(..., min_length=1, description="Question to answer")
    response_mode: ResponseMode = ResponseMode.DETAILED
    include_sources: bool = True
    filters: Optional[QueryFilters] = None


class SourceReference(BaseModel):
    """Source document reference in answer."""

    document_id: str
    filename: str
    section: Optional[str] = None


class AskResponse(BaseModel):
    """Ask (QA) response payload."""

    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    generation_time_ms: int
