"""Entity name extractor for identifying domain entities."""

import re
from typing import Optional

from src.core.extractors.base import BaseExtractor, ExtractedMetadata
from src.core.parsers.base import ParsedDocument, ContentType


class EntityExtractor(BaseExtractor):
    """Extractor for domain entity names and related concepts."""

    # Entity name patterns
    ENTITY_PATTERNS = [
        # Class/Interface definitions
        re.compile(r"(?:class|interface|struct|type)\s+(\w+)", re.IGNORECASE),
        # Entity mentions: "User entity", "the User model"
        re.compile(r"(\w+)\s+(?:entity|model|object|domain|aggregate)", re.IGNORECASE),
        # PascalCase words (likely entity names)
        re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b"),
        # Definition style: "User: represents..."
        re.compile(r"^(\w+)[:：]\s*(?:represents|表示|代表)", re.IGNORECASE | re.MULTILINE),
        # Markdown headers that look like entities
        re.compile(r"^#+\s*(\w+)\s*(?:Entity|Model|實體|模型)?$", re.IGNORECASE | re.MULTILINE),
    ]

    # Words that should not be considered entities
    EXCLUDED_WORDS = {
        # Common English words
        "the", "a", "an", "this", "that", "these", "those",
        "and", "or", "but", "for", "with", "from", "to",
        "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might",
        "get", "set", "create", "update", "delete", "read",
        # Technical terms
        "api", "http", "rest", "json", "xml", "sql",
        "database", "table", "column", "field", "schema",
        "request", "response", "endpoint", "method",
        "string", "integer", "boolean", "array", "object",
        "null", "undefined", "void", "any",
        "public", "private", "protected", "static",
        "class", "interface", "function", "method",
        # Common but not entities
        "example", "note", "warning", "info", "error",
        "version", "date", "time", "description",
    }

    # Common entity suffixes
    ENTITY_SUFFIXES = {
        "entity", "model", "dto", "vo", "do", "po",
        "record", "item", "entry", "data",
        "info", "detail", "summary",
        "request", "response",
    }

    def extract(self, document: ParsedDocument) -> ExtractedMetadata:
        """Extract entity names from a parsed document."""
        entities: set[str] = set()

        for section in document.sections:
            section_meta = self.extract_from_text(section.content)
            entities.update(section_meta.entity_names)

        return ExtractedMetadata(
            entity_names=sorted(list(entities)),
        )

    def extract_from_text(self, text: str) -> ExtractedMetadata:
        """Extract entity names from text content."""
        entities: set[str] = set()

        for pattern in self.ENTITY_PATTERNS:
            for match in pattern.finditer(text):
                entity = match.group(1)
                if self._is_valid_entity(entity):
                    entities.add(self._normalize_entity(entity))

        return ExtractedMetadata(
            entity_names=sorted(list(entities)),
        )

    def _is_valid_entity(self, name: str) -> bool:
        """Check if a name is a valid entity name."""
        # Must be at least 2 characters
        if len(name) < 2:
            return False

        # Must be alphanumeric
        if not name.isalnum():
            return False

        # Must not be in excluded words
        if name.lower() in self.EXCLUDED_WORDS:
            return False

        # Should start with uppercase (for PascalCase) or be a known pattern
        if not name[0].isupper() and not self._has_entity_suffix(name):
            return False

        # Should not be all uppercase (likely an acronym or constant)
        if name.isupper() and len(name) > 3:
            return False

        return True

    def _has_entity_suffix(self, name: str) -> bool:
        """Check if name has a common entity suffix."""
        name_lower = name.lower()
        return any(name_lower.endswith(suffix) for suffix in self.ENTITY_SUFFIXES)

    def _normalize_entity(self, name: str) -> str:
        """Normalize entity name to consistent format."""
        # Convert to PascalCase if not already
        if name[0].islower():
            name = name[0].upper() + name[1:]

        # Remove common suffixes for base entity name
        # (but keep the full name if it ends with these)
        # e.g., UserDTO -> UserDTO (not User)

        return name

    def extract_with_context(self, text: str) -> list[dict]:
        """Extract entities with surrounding context."""
        results = []

        for pattern in self.ENTITY_PATTERNS:
            for match in pattern.finditer(text):
                entity = match.group(1)
                if not self._is_valid_entity(entity):
                    continue

                # Get context (surrounding text)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()

                results.append({
                    "entity": self._normalize_entity(entity),
                    "context": context,
                    "position": match.start(),
                })

        return results
