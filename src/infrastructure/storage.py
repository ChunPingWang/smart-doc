"""File storage service for document management."""

import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import uuid4

from src.config import get_settings

settings = get_settings()


class FileStorage:
    """Local file storage service."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.upload_dir
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Ensure storage directory exists."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        file: BinaryIO,
        filename: str,
        document_id: Optional[str] = None,
    ) -> Path:
        """
        Save a file to storage.

        Returns the path to the saved file.
        """
        if document_id is None:
            document_id = f"doc_{uuid4().hex[:12]}"

        # Create document directory
        doc_dir = self.base_dir / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = doc_dir / filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file, f)

        return file_path

    def save_bytes(
        self,
        content: bytes,
        filename: str,
        document_id: Optional[str] = None,
    ) -> Path:
        """Save bytes content to storage."""
        if document_id is None:
            document_id = f"doc_{uuid4().hex[:12]}"

        doc_dir = self.base_dir / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        file_path = doc_dir / filename
        file_path.write_bytes(content)

        return file_path

    def get(self, document_id: str, filename: str) -> Optional[bytes]:
        """Get file content by document ID and filename."""
        file_path = self.base_dir / document_id / filename
        if file_path.exists():
            return file_path.read_bytes()
        return None

    def get_path(self, document_id: str, filename: str) -> Optional[Path]:
        """Get file path by document ID and filename."""
        file_path = self.base_dir / document_id / filename
        if file_path.exists():
            return file_path
        return None

    def delete(self, document_id: str) -> bool:
        """Delete all files for a document."""
        doc_dir = self.base_dir / document_id
        if doc_dir.exists():
            shutil.rmtree(doc_dir)
            return True
        return False

    def exists(self, document_id: str, filename: Optional[str] = None) -> bool:
        """Check if document or file exists."""
        if filename:
            return (self.base_dir / document_id / filename).exists()
        return (self.base_dir / document_id).is_dir()

    def list_documents(self) -> list[str]:
        """List all document IDs in storage."""
        return [
            d.name
            for d in self.base_dir.iterdir()
            if d.is_dir() and d.name.startswith("doc_")
        ]

    def get_size(self, document_id: str) -> int:
        """Get total size of files for a document in bytes."""
        doc_dir = self.base_dir / document_id
        if not doc_dir.exists():
            return 0

        total = 0
        for f in doc_dir.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total

    def get_total_size(self) -> int:
        """Get total storage size in bytes."""
        total = 0
        for f in self.base_dir.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total
