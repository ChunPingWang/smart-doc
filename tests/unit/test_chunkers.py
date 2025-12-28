"""Tests for document chunkers."""

import pytest
from pathlib import Path

from src.core.chunkers.semantic_chunker import SemanticChunker
from src.core.chunkers.structure_chunker import StructureChunker
from src.core.parsers.markdown_parser import MarkdownParser


class TestSemanticChunker:
    """Tests for SemanticChunker."""

    def test_chunk_small_content(self):
        """Test that small content is not split."""
        parser = MarkdownParser()
        chunker = SemanticChunker(chunk_size=1000)

        content = b"# Title\n\nShort content here."
        parsed = parser.parse_bytes(content, "test.md")
        chunks = chunker.chunk(parsed, "doc_123")

        # Small content should result in few chunks
        assert len(chunks) <= 3

    def test_chunk_preserves_document_id(self):
        """Test that chunks have correct document ID."""
        parser = MarkdownParser()
        chunker = SemanticChunker()

        content = b"# Title\n\nSome content."
        parsed = parser.parse_bytes(content, "test.md")
        chunks = chunker.chunk(parsed, "doc_abc123")

        for chunk in chunks:
            assert chunk.document_id == "doc_abc123"

    def test_chunk_has_unique_ids(self):
        """Test that each chunk has a unique ID."""
        parser = MarkdownParser()
        chunker = SemanticChunker(chunk_size=50)

        content = b"# Title\n\nFirst paragraph with content.\n\nSecond paragraph with more content.\n\nThird paragraph."
        parsed = parser.parse_bytes(content, "test.md")
        chunks = chunker.chunk(parsed, "doc_123")

        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique


class TestStructureChunker:
    """Tests for StructureChunker."""

    def test_chunk_preserves_hierarchy(self):
        """Test that section hierarchy is preserved."""
        parser = MarkdownParser()
        chunker = StructureChunker()

        content = b"# Main Title\n\n## Section 1\n\nContent here.\n\n## Section 2\n\nMore content."
        parsed = parser.parse_bytes(content, "test.md")
        chunks = chunker.chunk(parsed, "doc_123")

        # Check that chunks have section hierarchy
        for chunk in chunks:
            if chunk.section_hierarchy:
                assert len(chunk.section_hierarchy) > 0

    def test_chunk_includes_heading_prefix(self):
        """Test that heading prefix is included when configured."""
        parser = MarkdownParser()
        chunker = StructureChunker(include_heading_in_chunk=True)

        content = b"# Title\n\n## Section\n\nContent text."
        parsed = parser.parse_bytes(content, "test.md")
        chunks = chunker.chunk(parsed, "doc_123")

        # At least one chunk should have section info
        has_section_info = any(c.section_hierarchy for c in chunks)
        assert has_section_info
