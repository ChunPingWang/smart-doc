"""Structure-aware chunker that respects document hierarchy."""

from src.core.chunkers.base import BaseChunker, Chunk
from src.core.parsers.base import ParsedDocument, ParsedSection, ContentType


class StructureChunker(BaseChunker):
    """
    Chunker that preserves document structure.

    Groups content by headings and keeps related sections together.
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 100,
        min_chunk_size: int = 100,
        include_heading_in_chunk: bool = True,
    ):
        super().__init__(chunk_size, chunk_overlap)
        self.min_chunk_size = min_chunk_size
        self.include_heading_in_chunk = include_heading_in_chunk

    def chunk(
        self,
        document: ParsedDocument,
        document_id: str,
    ) -> list[Chunk]:
        """Split document into structure-aware chunks."""
        chunks: list[Chunk] = []

        # Group sections by heading hierarchy
        section_groups = self._group_sections_by_hierarchy(document.sections)

        for group_hierarchy, sections in section_groups:
            group_chunks = self._chunk_section_group(
                sections=sections,
                document_id=document_id,
                hierarchy=group_hierarchy,
            )
            chunks.extend(group_chunks)

        return chunks

    def _group_sections_by_hierarchy(
        self,
        sections: list[ParsedSection],
    ) -> list[tuple[list[str], list[ParsedSection]]]:
        """Group sections that share the same heading hierarchy."""
        groups: list[tuple[list[str], list[ParsedSection]]] = []
        current_hierarchy: list[str] = []
        current_sections: list[ParsedSection] = []

        for section in sections:
            # Skip heading sections (they're just markers)
            if section.content_type == ContentType.HEADING:
                # Start new group
                if current_sections:
                    groups.append((current_hierarchy.copy(), current_sections))
                    current_sections = []
                current_hierarchy = section.section_hierarchy.copy()
                continue

            # Check if hierarchy changed significantly
            if section.section_hierarchy != current_hierarchy:
                if current_sections:
                    groups.append((current_hierarchy.copy(), current_sections))
                    current_sections = []
                current_hierarchy = section.section_hierarchy.copy()

            current_sections.append(section)

        # Don't forget last group
        if current_sections:
            groups.append((current_hierarchy.copy(), current_sections))

        return groups

    def _chunk_section_group(
        self,
        sections: list[ParsedSection],
        document_id: str,
        hierarchy: list[str],
    ) -> list[Chunk]:
        """Chunk a group of sections that belong together."""
        chunks: list[Chunk] = []

        # Combine all content
        combined_parts: list[tuple[str, ContentType, dict]] = []
        for section in sections:
            metadata = {
                "heading_text": section.heading_text,
                "heading_level": section.heading_level,
                "code_language": section.code_language,
                "page_number": section.page_number,
            }
            combined_parts.append((section.content, section.content_type, metadata))

        # Calculate total size
        total_tokens = sum(self._count_tokens(p[0]) for p in combined_parts)

        # If small enough, create single chunk
        if total_tokens <= self.chunk_size:
            combined_content = "\n\n".join(p[0] for p in combined_parts)

            # Add heading prefix if configured
            if self.include_heading_in_chunk and hierarchy:
                heading_prefix = " > ".join(hierarchy) + "\n\n"
                combined_content = heading_prefix + combined_content

            chunks.append(
                Chunk.create(
                    document_id=document_id,
                    content=combined_content,
                    content_type=self._get_dominant_content_type(combined_parts),
                    section_hierarchy=hierarchy,
                    metadata=self._merge_metadata(combined_parts),
                )
            )
            return chunks

        # Need to split - process each part
        current_content: list[str] = []
        current_tokens = 0
        current_types: list[ContentType] = []

        for content, content_type, metadata in combined_parts:
            part_tokens = self._count_tokens(content)

            # If single part is too large, it needs special handling
            if part_tokens > self.chunk_size:
                # Save current chunk first
                if current_content:
                    chunk_content = "\n\n".join(current_content)
                    if self.include_heading_in_chunk and hierarchy:
                        chunk_content = " > ".join(hierarchy) + "\n\n" + chunk_content

                    chunks.append(
                        Chunk.create(
                            document_id=document_id,
                            content=chunk_content,
                            content_type=self._get_dominant_content_type_from_list(
                                current_types
                            ),
                            section_hierarchy=hierarchy,
                        )
                    )
                    current_content = []
                    current_tokens = 0
                    current_types = []

                # Split large content
                sub_chunks = self._split_large_content(
                    content, content_type, document_id, hierarchy
                )
                chunks.extend(sub_chunks)
                continue

            # Check if adding this part exceeds limit
            if current_tokens + part_tokens > self.chunk_size:
                # Save current chunk
                if current_content:
                    chunk_content = "\n\n".join(current_content)
                    if self.include_heading_in_chunk and hierarchy:
                        chunk_content = " > ".join(hierarchy) + "\n\n" + chunk_content

                    chunks.append(
                        Chunk.create(
                            document_id=document_id,
                            content=chunk_content,
                            content_type=self._get_dominant_content_type_from_list(
                                current_types
                            ),
                            section_hierarchy=hierarchy,
                        )
                    )
                    current_content = []
                    current_tokens = 0
                    current_types = []

            current_content.append(content)
            current_tokens += part_tokens
            current_types.append(content_type)

        # Don't forget last chunk
        if current_content:
            chunk_content = "\n\n".join(current_content)
            if self.include_heading_in_chunk and hierarchy:
                chunk_content = " > ".join(hierarchy) + "\n\n" + chunk_content

            chunks.append(
                Chunk.create(
                    document_id=document_id,
                    content=chunk_content,
                    content_type=self._get_dominant_content_type_from_list(current_types),
                    section_hierarchy=hierarchy,
                )
            )

        return chunks

    def _split_large_content(
        self,
        content: str,
        content_type: ContentType,
        document_id: str,
        hierarchy: list[str],
    ) -> list[Chunk]:
        """Split content that's too large for a single chunk."""
        chunks: list[Chunk] = []

        # For code blocks and tables, keep them as single chunks even if large
        if content_type in (ContentType.CODE_BLOCK, ContentType.TABLE):
            chunk_content = content
            if self.include_heading_in_chunk and hierarchy:
                chunk_content = " > ".join(hierarchy) + "\n\n" + chunk_content

            chunks.append(
                Chunk.create(
                    document_id=document_id,
                    content=chunk_content,
                    content_type=content_type,
                    section_hierarchy=hierarchy,
                )
            )
            return chunks

        # Split text content
        lines = content.split("\n")
        current_lines: list[str] = []
        current_tokens = 0

        for line in lines:
            line_tokens = self._count_tokens(line)

            if current_tokens + line_tokens > self.chunk_size:
                if current_lines:
                    chunk_content = "\n".join(current_lines)
                    if self.include_heading_in_chunk and hierarchy:
                        chunk_content = " > ".join(hierarchy) + "\n\n" + chunk_content

                    chunks.append(
                        Chunk.create(
                            document_id=document_id,
                            content=chunk_content,
                            content_type=content_type,
                            section_hierarchy=hierarchy,
                        )
                    )
                    current_lines = []
                    current_tokens = 0

            current_lines.append(line)
            current_tokens += line_tokens

        # Last chunk
        if current_lines:
            chunk_content = "\n".join(current_lines)
            if self.include_heading_in_chunk and hierarchy:
                chunk_content = " > ".join(hierarchy) + "\n\n" + chunk_content

            chunks.append(
                Chunk.create(
                    document_id=document_id,
                    content=chunk_content,
                    content_type=content_type,
                    section_hierarchy=hierarchy,
                )
            )

        return chunks

    def _get_dominant_content_type(
        self,
        parts: list[tuple[str, ContentType, dict]],
    ) -> ContentType:
        """Get the most common content type from parts."""
        return self._get_dominant_content_type_from_list([p[1] for p in parts])

    def _get_dominant_content_type_from_list(
        self,
        types: list[ContentType],
    ) -> ContentType:
        """Get the most common content type from a list."""
        if not types:
            return ContentType.TEXT

        # Priority: CODE_BLOCK > TABLE > LIST > TEXT
        priority = {
            ContentType.CODE_BLOCK: 4,
            ContentType.TABLE: 3,
            ContentType.LIST: 2,
            ContentType.TEXT: 1,
            ContentType.HEADING: 0,
        }

        return max(types, key=lambda t: priority.get(t, 0))

    def _merge_metadata(
        self,
        parts: list[tuple[str, ContentType, dict]],
    ) -> dict:
        """Merge metadata from multiple parts."""
        merged = {}
        for _, _, metadata in parts:
            for key, value in metadata.items():
                if value is not None:
                    if key not in merged:
                        merged[key] = value
        return merged
