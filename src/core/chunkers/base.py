"""Base chunker interface and data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

from src.core.parsers.base import ParsedDocument, ContentType


@dataclass
class Chunk:
    """A chunk of document content for indexing."""

    chunk_id: str
    document_id: str
    content: str
    content_type: ContentType
    section_hierarchy: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: Optional[list[float]] = None

    @classmethod
    def create(
        cls,
        document_id: str,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        **kwargs: Any,
    ) -> "Chunk":
        """Factory method to create a chunk with auto-generated ID."""
        return cls(
            chunk_id=f"chunk_{uuid4().hex[:12]}",
            document_id=document_id,
            content=content,
            content_type=content_type,
            **kwargs,
        )

    def to_payload(self) -> dict[str, Any]:
        """Convert to vector store payload format."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "content_type": self.content_type.value,
            "section_hierarchy": self.section_hierarchy,
            **self.metadata,
        }


class BaseChunker(ABC):
    """Abstract base class for document chunkers."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(
        self,
        document: ParsedDocument,
        document_id: str,
    ) -> list[Chunk]:
        """
        Split a parsed document into chunks.

        Args:
            document: The parsed document to chunk
            document_id: Unique identifier for the document

        Returns:
            List of Chunk objects
        """
        pass

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters for English
        # For Chinese, 1 token ≈ 1-2 characters
        return len(text) // 3
