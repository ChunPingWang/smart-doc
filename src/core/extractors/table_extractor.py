"""Table schema extractor for database schema documents."""

import re
from typing import Any, Optional

from src.core.extractors.base import BaseExtractor, ExtractedMetadata
from src.core.parsers.base import ParsedDocument, ContentType


class TableExtractor(BaseExtractor):
    """Extractor for database table schemas and column definitions."""

    # Table name patterns
    TABLE_NAME_PATTERNS = [
        # Table: users
        re.compile(r"(?:table|表格?)[:：\s]+[`'\"]?(\w+)[`'\"]?", re.IGNORECASE),
        # CREATE TABLE users
        re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`'\"]?(\w+)[`'\"]?", re.IGNORECASE),
        # ## users table
        re.compile(r"^#+\s*(\w+)\s*(?:table|表)", re.IGNORECASE | re.MULTILINE),
        # Sheet name that looks like a table
        re.compile(r"(?:sheet|工作表)[:：\s]+(\w+)", re.IGNORECASE),
    ]

    # Common SQL data types
    SQL_TYPES = {
        "int", "integer", "bigint", "smallint", "tinyint",
        "varchar", "char", "text", "longtext", "mediumtext",
        "decimal", "numeric", "float", "double", "real",
        "date", "datetime", "timestamp", "time",
        "boolean", "bool", "bit",
        "blob", "binary", "varbinary",
        "json", "jsonb", "xml",
        "uuid", "serial", "bigserial",
    }

    # Column definition pattern (from CREATE TABLE)
    COLUMN_PATTERN = re.compile(
        r"[`'\"]?(\w+)[`'\"]?\s+"
        r"((?:VARCHAR|CHAR|INT|INTEGER|BIGINT|DECIMAL|NUMERIC|FLOAT|DOUBLE|"
        r"TEXT|DATE|DATETIME|TIMESTAMP|BOOLEAN|BOOL|JSON|UUID|SERIAL)[\w\(\),\s]*)",
        re.IGNORECASE,
    )

    def extract(self, document: ParsedDocument) -> ExtractedMetadata:
        """Extract table schemas from a parsed document."""
        table_names: set[str] = set()
        column_definitions: list[dict[str, Any]] = []

        for section in document.sections:
            # Check section metadata for table info (from Excel parser)
            if section.metadata.get("is_schema_table"):
                sheet_name = section.metadata.get("sheet_name", "")
                if sheet_name:
                    table_names.add(sheet_name.lower())

                columns = section.metadata.get("columns", [])
                if columns:
                    column_definitions.append({
                        "table": sheet_name,
                        "columns": columns,
                    })

            # Extract from content
            section_meta = self.extract_from_text(section.content)
            table_names.update(section_meta.table_names)
            column_definitions.extend(section_meta.column_definitions)

        return ExtractedMetadata(
            table_names=sorted(list(table_names)),
            column_definitions=column_definitions,
        )

    def extract_from_text(self, text: str) -> ExtractedMetadata:
        """Extract table schemas from text content."""
        table_names: set[str] = set()
        column_definitions: list[dict[str, Any]] = []

        # Extract table names
        for pattern in self.TABLE_NAME_PATTERNS:
            for match in pattern.finditer(text):
                table_name = match.group(1).lower()
                # Filter out common false positives
                if not self._is_valid_table_name(table_name):
                    continue
                table_names.add(table_name)

        # Extract column definitions from CREATE TABLE
        create_table_pattern = re.compile(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`'\"]?(\w+)[`'\"]?\s*\((.*?)\)",
            re.IGNORECASE | re.DOTALL,
        )

        for match in create_table_pattern.finditer(text):
            table_name = match.group(1).lower()
            table_names.add(table_name)

            columns_text = match.group(2)
            columns = self._parse_columns(columns_text)
            if columns:
                column_definitions.append({
                    "table": table_name,
                    "columns": columns,
                })

        # Extract from Markdown tables
        md_columns = self._extract_from_markdown_table(text)
        if md_columns:
            column_definitions.extend(md_columns)

        return ExtractedMetadata(
            table_names=sorted(list(table_names)),
            column_definitions=column_definitions,
        )

    def _is_valid_table_name(self, name: str) -> bool:
        """Check if a name looks like a valid table name."""
        # Must be alphanumeric with underscores
        if not re.match(r"^\w+$", name):
            return False

        # Filter out common false positives
        invalid_names = {
            "the", "a", "an", "this", "that", "table", "schema",
            "column", "field", "name", "type", "description",
            "create", "select", "insert", "update", "delete",
        }
        return name.lower() not in invalid_names

    def _parse_columns(self, columns_text: str) -> list[dict[str, Any]]:
        """Parse column definitions from CREATE TABLE body."""
        columns = []

        for match in self.COLUMN_PATTERN.finditer(columns_text):
            column_name = match.group(1)
            column_type = match.group(2).strip()

            # Check for constraints
            is_nullable = "NOT NULL" not in columns_text.upper()
            is_primary = "PRIMARY KEY" in columns_text.upper()

            columns.append({
                "name": column_name,
                "type": column_type,
                "nullable": is_nullable,
                "primary_key": is_primary,
            })

        return columns

    def _extract_from_markdown_table(self, text: str) -> list[dict[str, Any]]:
        """Extract column definitions from Markdown tables."""
        results = []

        # Find Markdown tables
        table_pattern = re.compile(
            r"\|([^\n]+)\|\n\|[-:\s|]+\|\n((?:\|[^\n]+\|\n?)+)",
            re.MULTILINE,
        )

        for match in table_pattern.finditer(text):
            header_line = match.group(1)
            headers = [h.strip() for h in header_line.split("|") if h.strip()]

            # Check if this looks like a schema table
            header_lower = [h.lower() for h in headers]
            schema_keywords = {"column", "field", "name", "type", "datatype", "description"}
            if not any(kw in " ".join(header_lower) for kw in schema_keywords):
                continue

            body = match.group(2)
            rows = body.strip().split("\n")

            columns = []
            for row in rows:
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if len(cells) >= 2:
                    columns.append({
                        "name": cells[0],
                        "type": cells[1] if len(cells) > 1 else "",
                        "description": cells[2] if len(cells) > 2 else "",
                    })

            if columns:
                results.append({"columns": columns})

        return results
