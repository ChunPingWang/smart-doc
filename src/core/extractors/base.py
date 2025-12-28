"""Base extractor interface and data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from src.core.parsers.base import ParsedDocument


@dataclass
class ExtractedMetadata:
    """Container for extracted metadata from a document."""

    # API-related
    api_endpoints: list[str] = field(default_factory=list)
    http_methods: list[str] = field(default_factory=list)

    # Table/Schema-related
    table_names: list[str] = field(default_factory=list)
    column_definitions: list[dict[str, Any]] = field(default_factory=list)

    # Entity-related
    entity_names: list[str] = field(default_factory=list)

    # Code-related
    code_languages: list[str] = field(default_factory=list)

    # Additional extracted info
    extra: dict[str, Any] = field(default_factory=dict)

    def merge(self, other: "ExtractedMetadata") -> "ExtractedMetadata":
        """Merge with another ExtractedMetadata."""
        return ExtractedMetadata(
            api_endpoints=list(set(self.api_endpoints + other.api_endpoints)),
            http_methods=list(set(self.http_methods + other.http_methods)),
            table_names=list(set(self.table_names + other.table_names)),
            column_definitions=self.column_definitions + other.column_definitions,
            entity_names=list(set(self.entity_names + other.entity_names)),
            code_languages=list(set(self.code_languages + other.code_languages)),
            extra={**self.extra, **other.extra},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "api_endpoints": self.api_endpoints,
            "http_methods": self.http_methods,
            "table_names": self.table_names,
            "entity_names": self.entity_names,
            "code_languages": self.code_languages,
        }


class BaseExtractor(ABC):
    """Abstract base class for metadata extractors."""

    @abstractmethod
    def extract(self, document: ParsedDocument) -> ExtractedMetadata:
        """
        Extract metadata from a parsed document.

        Args:
            document: The parsed document to extract from

        Returns:
            ExtractedMetadata containing all extracted information
        """
        pass

    @abstractmethod
    def extract_from_text(self, text: str) -> ExtractedMetadata:
        """
        Extract metadata from raw text.

        Args:
            text: The text content to extract from

        Returns:
            ExtractedMetadata containing all extracted information
        """
        pass
