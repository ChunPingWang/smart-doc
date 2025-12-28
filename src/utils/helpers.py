"""General utility functions."""

import hashlib
from uuid import uuid4


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_part = uuid4().hex[:12]
    if prefix:
        return f"{prefix}_{unique_part}"
    return unique_part


def calculate_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of content."""
    return hashlib.sha256(content).hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def clean_filename(filename: str) -> str:
    """Clean filename for safe storage."""
    # Remove path components
    filename = filename.replace("/", "_").replace("\\", "_")
    # Remove problematic characters
    unsafe_chars = '<>:"|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")
    return filename


def format_bytes(size: int) -> str:
    """Format byte size to human readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"
