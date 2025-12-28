"""Base generator interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from src.core.retrievers.base import RetrievalResult


@dataclass
class GeneratedResponse:
    """A generated response with metadata."""

    content: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseGenerator(ABC):
    """Abstract base class for response generators."""

    @abstractmethod
    async def generate(
        self,
        query: str,
        context: list[RetrievalResult],
        **kwargs: Any,
    ) -> GeneratedResponse:
        """
        Generate a response based on query and retrieved context.

        Args:
            query: The user's question or query
            context: Retrieved document chunks for context
            **kwargs: Additional generation parameters

        Returns:
            GeneratedResponse with content and metadata
        """
        pass
