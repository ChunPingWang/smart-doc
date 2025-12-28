"""Markdown document parser."""

import re
from pathlib import Path
from typing import Optional

from src.core.parsers.base import (
    BaseParser,
    ContentType,
    ParsedDocument,
    ParsedSection,
)


class MarkdownParser(BaseParser):
    """Parser for Markdown (.md) files."""

    SUPPORTED_EXTENSIONS = {".md", ".markdown"}

    # Regex patterns
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    TABLE_PATTERN = re.compile(r"(\|[^\n]+\|\n)+", re.MULTILINE)
    LIST_PATTERN = re.compile(r"^(\s*[-*+]|\s*\d+\.)\s+.+$", re.MULTILINE)

    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse a Markdown file."""
        content = file_path.read_text(encoding="utf-8")
        return self._parse_content(content, file_path.name, file_path)

    def parse_bytes(self, content: bytes, filename: str) -> ParsedDocument:
        """Parse Markdown from bytes."""
        text = content.decode("utf-8")
        return self._parse_content(text, filename, Path(filename))

    def _parse_content(
        self,
        content: str,
        filename: str,
        file_path: Path,
    ) -> ParsedDocument:
        """Parse Markdown content into sections."""
        sections: list[ParsedSection] = []
        current_hierarchy: list[str] = []

        # Extract code blocks first (to avoid parsing them as other content)
        code_blocks: dict[str, tuple[str, str]] = {}
        code_idx = 0

        def replace_code_block(match: re.Match) -> str:
            nonlocal code_idx
            placeholder = f"__CODE_BLOCK_{code_idx}__"
            code_blocks[placeholder] = (match.group(1), match.group(2))
            code_idx += 1
            return placeholder

        # Replace code blocks with placeholders
        content_no_code = self.CODE_BLOCK_PATTERN.sub(replace_code_block, content)

        # Split by headings
        lines = content_no_code.split("\n")
        current_section_lines: list[str] = []
        current_heading: Optional[str] = None
        current_level: Optional[int] = None

        for line in lines:
            heading_match = self.HEADING_PATTERN.match(line)

            if heading_match:
                # Save previous section if exists
                if current_section_lines or current_heading:
                    section_content = "\n".join(current_section_lines).strip()
                    if section_content or current_heading:
                        sections.extend(
                            self._create_sections_from_content(
                                section_content,
                                current_heading,
                                current_level,
                                current_hierarchy.copy(),
                                code_blocks,
                            )
                        )

                # Update hierarchy
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()

                # Adjust hierarchy based on level
                while len(current_hierarchy) >= level:
                    current_hierarchy.pop()
                current_hierarchy.append(heading_text)

                current_heading = heading_text
                current_level = level
                current_section_lines = []

                # Add heading as a section
                sections.append(
                    ParsedSection(
                        content=line,
                        content_type=ContentType.HEADING,
                        heading_level=level,
                        heading_text=heading_text,
                        section_hierarchy=current_hierarchy.copy(),
                    )
                )
            else:
                current_section_lines.append(line)

        # Don't forget the last section
        if current_section_lines:
            section_content = "\n".join(current_section_lines).strip()
            if section_content:
                sections.extend(
                    self._create_sections_from_content(
                        section_content,
                        current_heading,
                        current_level,
                        current_hierarchy.copy(),
                        code_blocks,
                    )
                )

        return ParsedDocument(
            filename=filename,
            file_path=file_path,
            sections=sections,
            metadata=self._extract_metadata(content),
            raw_text=content,
        )

    def _create_sections_from_content(
        self,
        content: str,
        heading: Optional[str],
        level: Optional[int],
        hierarchy: list[str],
        code_blocks: dict[str, tuple[str, str]],
    ) -> list[ParsedSection]:
        """Create sections from content, handling code blocks and tables."""
        sections: list[ParsedSection] = []

        # Replace code block placeholders and create code sections
        for placeholder, (lang, code) in code_blocks.items():
            if placeholder in content:
                # Split around the placeholder
                parts = content.split(placeholder)
                before = parts[0].strip()
                after = parts[1].strip() if len(parts) > 1 else ""

                if before:
                    sections.append(
                        ParsedSection(
                            content=before,
                            content_type=self._detect_content_type(before),
                            heading_text=heading,
                            heading_level=level,
                            section_hierarchy=hierarchy,
                        )
                    )

                # Add code block section
                sections.append(
                    ParsedSection(
                        content=code.strip(),
                        content_type=ContentType.CODE_BLOCK,
                        heading_text=heading,
                        heading_level=level,
                        section_hierarchy=hierarchy,
                        code_language=lang or None,
                    )
                )

                content = after

        # Add remaining content
        if content.strip():
            sections.append(
                ParsedSection(
                    content=content,
                    content_type=self._detect_content_type(content),
                    heading_text=heading,
                    heading_level=level,
                    section_hierarchy=hierarchy,
                )
            )

        return sections

    def _detect_content_type(self, content: str) -> ContentType:
        """Detect the type of content."""
        if self.TABLE_PATTERN.search(content):
            return ContentType.TABLE
        if self.LIST_PATTERN.search(content):
            return ContentType.LIST
        return ContentType.TEXT

    def _extract_metadata(self, content: str) -> dict:
        """Extract metadata from Markdown content."""
        metadata = {}

        # Extract YAML front matter if present
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                front_matter = content[3:end].strip()
                metadata["front_matter"] = front_matter

        # Count elements
        metadata["heading_count"] = len(self.HEADING_PATTERN.findall(content))
        metadata["code_block_count"] = len(self.CODE_BLOCK_PATTERN.findall(content))
        metadata["table_count"] = len(self.TABLE_PATTERN.findall(content))

        return metadata
