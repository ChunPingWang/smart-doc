"""Base retriever interface and data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RetrievalResult:
    """A single retrieval result."""

    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"  # e.g., "dense", "sparse", "hybrid"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "source": self.source,
        }


class BaseRetriever(ABC):
    """Abstract base class for document retrievers."""

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: The search query
            top_k: Number of results to return
            filters: Optional filters (doc_types, tags, etc.)

        Returns:
            List of RetrievalResult objects sorted by relevance
        """
        pass

    @abstractmethod
    async def aretrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Async version of retrieve."""
        pass
