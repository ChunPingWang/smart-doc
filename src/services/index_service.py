"""Index management service."""

from datetime import datetime
from typing import Any, Optional

import structlog

from src.api.schemas import DocumentStats
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.storage import FileStorage

logger = structlog.get_logger()


class IndexService:
    """Service for managing document indexes."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        file_storage: Optional[FileStorage] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.file_storage = file_storage or FileStorage()

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        try:
            collection_info = self.vector_store.get_collection_info()
            vectors_count = collection_info.get("vectors_count", 0)
        except Exception:
            vectors_count = 0

        # Get document count from file storage
        document_ids = self.file_storage.list_documents()
        total_documents = len(document_ids)

        # Calculate storage usage
        storage_bytes = self.file_storage.get_total_size()
        storage_mb = storage_bytes / (1024 * 1024)

        return {
            "total_documents": total_documents,
            "total_chunks": vectors_count,
            "documents_by_type": DocumentStats(),  # Would need document registry
            "storage_used_mb": round(storage_mb, 2),
            "last_indexed_at": None,  # Would need to track this
        }

    def health_check(self) -> dict[str, Any]:
        """Check health of all index components."""
        components = {}

        # Vector store health
        try:
            is_healthy = self.vector_store.health_check()
            components["vector_store"] = {
                "status": "healthy" if is_healthy else "unhealthy",
            }
        except Exception as e:
            components["vector_store"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # File storage health
        try:
            # Just check if upload dir exists
            upload_dir = self.file_storage.base_dir
            if upload_dir.exists():
                components["file_storage"] = {"status": "healthy"}
            else:
                components["file_storage"] = {
                    "status": "unhealthy",
                    "error": "Upload directory does not exist",
                }
        except Exception as e:
            components["file_storage"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Overall status
        all_healthy = all(c["status"] == "healthy" for c in components.values())
        overall_status = "healthy" if all_healthy else "degraded"

        return {
            "status": overall_status,
            "components": components,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def initialize(self) -> None:
        """Initialize the index (create collections, etc.)."""
        logger.info("Initializing index")

        # Ensure vector store collection exists
        self.vector_store.ensure_collection()

        # Ensure upload directory exists
        self.file_storage._ensure_dir()

        logger.info("Index initialized successfully")

    def rebuild_all(self) -> dict[str, Any]:
        """Rebuild all indexes from stored documents."""
        # This would require a document registry to track all documents
        raise NotImplementedError(
            "Full rebuild requires document registry implementation"
        )

    def optimize(self) -> None:
        """Optimize the index for better query performance."""
        # Qdrant handles optimization automatically
        # This could be used for manual optimization if needed
        logger.info("Index optimization requested (no-op for Qdrant)")
