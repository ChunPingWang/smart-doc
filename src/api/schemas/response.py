"""Common response schemas."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    status: str = "error"
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class ComponentHealth(BaseModel):
    """Health status of a component."""

    status: str
    latency_ms: Optional[int] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    components: dict[str, ComponentHealth]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentStats(BaseModel):
    """Document statistics by type."""

    api_spec: int = 0
    table_schema: int = 0
    system_design: int = 0
    general: int = 0


class StatsResponse(BaseModel):
    """System statistics response."""

    total_documents: int
    total_chunks: int
    documents_by_type: DocumentStats
    storage_used_mb: float
    last_indexed_at: Optional[datetime] = None
