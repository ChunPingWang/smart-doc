"""Document-related Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DocType(str, Enum):
    """Document type classification."""

    API_SPEC = "api_spec"
    TABLE_SCHEMA = "table_schema"
    SYSTEM_DESIGN = "system_design"
    GENERAL = "general"


class IndexStatus(str, Enum):
    """Document indexing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Extracted metadata from document."""

    api_endpoints: list[str] = Field(default_factory=list)
    table_names: list[str] = Field(default_factory=list)
    entity_names: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    """Document information response."""

    document_id: str
    filename: str
    doc_type: DocType
    chunks_count: int
    file_size: int
    status: IndexStatus
    tags: list[str] = Field(default_factory=list)
    metadata: Optional[DocumentMetadata] = None
    created_at: datetime
    updated_at: datetime
    indexed_at: Optional[datetime] = None


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""

    document_id: str
    filename: str
    doc_type: DocType
    chunks_count: int
    metadata: DocumentMetadata
    created_at: datetime


class PaginatedDocuments(BaseModel):
    """Paginated list of documents."""

    items: list[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int
