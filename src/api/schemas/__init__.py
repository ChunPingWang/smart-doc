"""Pydantic schemas for API request/response models."""

from src.api.schemas.document import (
    DocType,
    DocumentMetadata,
    DocumentResponse,
    DocumentUploadResponse,
    IndexStatus,
    PaginatedDocuments,
)
from src.api.schemas.query import (
    CrossReference,
    QueryFilters,
    QueryRequest,
    ResponseMode,
    SearchRequest,
    SearchResult,
    SearchResponse,
    AskRequest,
    AskResponse,
    SourceReference,
)
from src.api.schemas.response import (
    APIResponse,
    ErrorResponse,
    HealthResponse,
    ComponentHealth,
    StatsResponse,
    DocumentStats,
)

__all__ = [
    # Document
    "DocType",
    "IndexStatus",
    "DocumentMetadata",
    "DocumentResponse",
    "DocumentUploadResponse",
    "PaginatedDocuments",
    # Query
    "QueryFilters",
    "QueryRequest",
    "ResponseMode",
    "SearchRequest",
    "SearchResult",
    "CrossReference",
    "SearchResponse",
    "AskRequest",
    "AskResponse",
    "SourceReference",
    # Response
    "APIResponse",
    "ErrorResponse",
    "HealthResponse",
    "ComponentHealth",
    "StatsResponse",
    "DocumentStats",
]
