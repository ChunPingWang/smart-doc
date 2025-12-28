"""Tests for document parsers."""

import pytest
from pathlib import Path

from src.core.parsers.markdown_parser import MarkdownParser
from src.core.parsers.base import ContentType


class TestMarkdownParser:
    """Tests for MarkdownParser."""

    def test_can_parse_md_extension(self):
        """Test that parser recognizes .md files."""
        parser = MarkdownParser()
        assert parser.can_parse(Path("test.md"))
        assert parser.can_parse(Path("test.markdown"))
        assert not parser.can_parse(Path("test.txt"))

    def test_parse_basic_content(self, sample_markdown: str):
        """Test parsing basic markdown content."""
        parser = MarkdownParser()
        content = sample_markdown.encode("utf-8")
        result = parser.parse_bytes(content, "test.md")

        assert result.filename == "test.md"
        assert len(result.sections) > 0

    def test_parse_headings(self):
        """Test heading extraction."""
        parser = MarkdownParser()
        content = b"# Title\n\n## Section 1\n\nContent\n\n## Section 2\n\nMore content"
        result = parser.parse_bytes(content, "test.md")

        headings = [s for s in result.sections if s.content_type == ContentType.HEADING]
        assert len(headings) == 3  # Title, Section 1, Section 2

    def test_parse_code_blocks(self):
        """Test code block extraction."""
        parser = MarkdownParser()
        content = b"# Code Example\n\n```python\nprint('hello')\n```\n"
        result = parser.parse_bytes(content, "test.md")

        code_blocks = [s for s in result.sections if s.content_type == ContentType.CODE_BLOCK]
        assert len(code_blocks) == 1
        assert "print" in code_blocks[0].content

    def test_section_hierarchy(self):
        """Test section hierarchy tracking."""
        parser = MarkdownParser()
        content = b"# Level 1\n\n## Level 2\n\nText\n\n### Level 3\n\nMore text"
        result = parser.parse_bytes(content, "test.md")

        # Find the Level 3 heading
        level3 = None
        for section in result.sections:
            if section.heading_text == "Level 3":
                level3 = section
                break

        assert level3 is not None
        assert "Level 1" in level3.section_hierarchy
        assert "Level 2" in level3.section_hierarchy


class TestAPIExtraction:
    """Tests for API endpoint extraction from markdown."""

    def test_extract_endpoints(self, sample_api_spec: str):
        """Test extraction of API endpoints."""
        from src.core.extractors.api_extractor import APIExtractor

        extractor = APIExtractor()
        result = extractor.extract_from_text(sample_api_spec)

        assert len(result.api_endpoints) > 0
        assert any("GET" in ep for ep in result.api_endpoints)
        assert any("POST" in ep for ep in result.api_endpoints)
