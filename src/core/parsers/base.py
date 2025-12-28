"""Base parser interface and data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ContentType(str, Enum):
    """Content type classification."""

    TEXT = "text"
    TABLE = "table"
    CODE_BLOCK = "code_block"
    LIST = "list"
    HEADING = "heading"


@dataclass
class ParsedSection:
    """A parsed section from a document."""

    content: str
    content_type: ContentType
    heading_level: Optional[int] = None
    heading_text: Optional[str] = None
    section_hierarchy: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    page_number: Optional[int] = None
    code_language: Optional[str] = None


@dataclass
class ParsedDocument:
    """A fully parsed document."""

    filename: str
    file_path: Path
    sections: list[ParsedSection]
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_text: Optional[str] = None

    @property
    def full_text(self) -> str:
        """Get concatenated text from all sections."""
        return "\n\n".join(s.content for s in self.sections)

    @property
    def section_count(self) -> int:
        """Get number of sections."""
        return len(self.sections)


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    SUPPORTED_EXTENSIONS: set[str] = set()

    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if this parser can handle the file."""
        return file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a document file.

        Args:
            file_path: Path to the document file

        Returns:
            ParsedDocument with extracted sections and metadata
        """
        pass

    @abstractmethod
    def parse_bytes(self, content: bytes, filename: str) -> ParsedDocument:
        """
        Parse document from bytes content.

        Args:
            content: File content as bytes
            filename: Original filename for type detection

        Returns:
            ParsedDocument with extracted sections and metadata
        """
        pass


def get_parser_for_file(file_path: Path) -> Optional[BaseParser]:
    """Get appropriate parser for a file."""
    from src.core.parsers.markdown_parser import MarkdownParser
    from src.core.parsers.word_parser import WordParser
    from src.core.parsers.excel_parser import ExcelParser

    parsers = [MarkdownParser(), WordParser(), ExcelParser()]

    for parser in parsers:
        if parser.can_parse(file_path):
            return parser

    return None
