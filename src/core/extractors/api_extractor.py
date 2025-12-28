"""API endpoint extractor for API specification documents."""

import re
from typing import Optional

from src.core.extractors.base import BaseExtractor, ExtractedMetadata
from src.core.parsers.base import ParsedDocument, ContentType


class APIExtractor(BaseExtractor):
    """Extractor for API endpoints and related metadata."""

    # HTTP method patterns
    HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}

    # Common API endpoint patterns
    ENDPOINT_PATTERNS = [
        # Markdown: ## GET /api/users
        re.compile(
            r"(?:^|\n)#+\s*(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\n]+)",
            re.IGNORECASE,
        ),
        # Plain: GET /api/users
        re.compile(
            r"(?:^|\n)\s*(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(/[^\s\n]+)",
            re.IGNORECASE,
        ),
        # REST style: /api/users (GET)
        re.compile(
            r"(/api/[^\s\n\)]+)\s*\((GET|POST|PUT|DELETE|PATCH)\)",
            re.IGNORECASE,
        ),
        # Endpoint line: `GET /api/users`
        re.compile(
            r"`(GET|POST|PUT|DELETE|PATCH)\s+(/[^`]+)`",
            re.IGNORECASE,
        ),
        # URL with method in context
        re.compile(
            r"(?:endpoint|api|route|path)[:：]\s*(GET|POST|PUT|DELETE|PATCH)?\s*(/[^\s\n]+)",
            re.IGNORECASE,
        ),
    ]

    # Path parameter pattern
    PATH_PARAM_PATTERN = re.compile(r"\{(\w+)\}|:(\w+)")

    def extract(self, document: ParsedDocument) -> ExtractedMetadata:
        """Extract API endpoints from a parsed document."""
        endpoints: set[str] = set()
        methods: set[str] = set()

        for section in document.sections:
            section_meta = self.extract_from_text(section.content)
            endpoints.update(section_meta.api_endpoints)
            methods.update(section_meta.http_methods)

        return ExtractedMetadata(
            api_endpoints=sorted(list(endpoints)),
            http_methods=sorted(list(methods)),
        )

    def extract_from_text(self, text: str) -> ExtractedMetadata:
        """Extract API endpoints from text content."""
        endpoints: set[str] = set()
        methods: set[str] = set()

        for pattern in self.ENDPOINT_PATTERNS:
            for match in pattern.finditer(text):
                groups = match.groups()

                # Different patterns have different group orders
                method = None
                path = None

                for group in groups:
                    if group:
                        if group.upper() in self.HTTP_METHODS:
                            method = group.upper()
                        elif group.startswith("/"):
                            path = self._normalize_path(group)

                if path:
                    if method:
                        endpoints.add(f"{method} {path}")
                        methods.add(method)
                    else:
                        endpoints.add(path)

        return ExtractedMetadata(
            api_endpoints=sorted(list(endpoints)),
            http_methods=sorted(list(methods)),
        )

    def _normalize_path(self, path: str) -> str:
        """Normalize API path."""
        # Remove trailing punctuation
        path = path.rstrip(".,;:)")

        # Normalize path parameters
        # {id} and :id -> {id}
        path = re.sub(r":(\w+)", r"{\1}", path)

        return path

    def extract_path_params(self, endpoint: str) -> list[str]:
        """Extract path parameters from an endpoint."""
        params = []
        for match in self.PATH_PARAM_PATTERN.finditer(endpoint):
            param = match.group(1) or match.group(2)
            if param:
                params.append(param)
        return params

    def parse_endpoint(self, endpoint: str) -> dict:
        """Parse an endpoint string into components."""
        result = {
            "method": None,
            "path": endpoint,
            "path_params": [],
        }

        # Check if method is included
        parts = endpoint.split(" ", 1)
        if len(parts) == 2 and parts[0].upper() in self.HTTP_METHODS:
            result["method"] = parts[0].upper()
            result["path"] = parts[1]

        # Extract path parameters
        result["path_params"] = self.extract_path_params(result["path"])

        return result
