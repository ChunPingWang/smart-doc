"""Document processing service."""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import structlog

from src.api.schemas import DocType, DocumentMetadata, IndexStatus
from src.core.parsers.base import get_parser_for_file, ParsedDocument
from src.core.chunkers.base import Chunk
from src.core.chunkers.structure_chunker import StructureChunker
from src.core.extractors.api_extractor import APIExtractor
from src.core.extractors.table_extractor import TableExtractor
from src.core.extractors.entity_extractor import EntityExtractor
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.embedding import EmbeddingService
from src.infrastructure.storage import FileStorage

logger = structlog.get_logger()


class DocumentService:
    """Service for document processing and indexing."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        file_storage: Optional[FileStorage] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService()
        self.file_storage = file_storage or FileStorage()

        # Initialize extractors
        self.api_extractor = APIExtractor()
        self.table_extractor = TableExtractor()
        self.entity_extractor = EntityExtractor()

        # Initialize chunker
        self.chunker = StructureChunker()

    def process_document(
        self,
        content: bytes,
        filename: str,
        doc_type: Optional[DocType] = None,
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Process and index a document.

        Args:
            content: File content as bytes
            filename: Original filename
            doc_type: Document type (optional, will be auto-detected)
            tags: Tags for the document

        Returns:
            Document info including ID, chunks count, metadata
        """
        document_id = f"doc_{uuid4().hex[:12]}"
        logger.info("Processing document", document_id=document_id, filename=filename)

        try:
            # Save file to storage
            file_path = self.file_storage.save_bytes(content, filename, document_id)

            # Parse document
            parsed = self._parse_document(file_path, content, filename)

            # Auto-detect document type if not provided
            if doc_type is None:
                doc_type = self._detect_doc_type(parsed)

            # Extract metadata
            metadata = self._extract_metadata(parsed)

            # Chunk document
            chunks = self.chunker.chunk(parsed, document_id)

            # Add doc_type and tags to chunk metadata
            for chunk in chunks:
                chunk.metadata["doc_type"] = doc_type.value
                chunk.metadata["tags"] = tags or []
                chunk.metadata["filename"] = filename

            # Generate embeddings and store
            self._store_chunks(chunks)

            logger.info(
                "Document processed successfully",
                document_id=document_id,
                chunks_count=len(chunks),
            )

            return {
                "document_id": document_id,
                "filename": filename,
                "doc_type": doc_type,
                "chunks_count": len(chunks),
                "file_size": len(content),
                "status": IndexStatus.INDEXED,
                "metadata": metadata,
                "tags": tags or [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "indexed_at": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(
                "Failed to process document",
                document_id=document_id,
                error=str(e),
            )
            raise

    def _parse_document(
        self,
        file_path: Path,
        content: bytes,
        filename: str,
    ) -> ParsedDocument:
        """Parse document using appropriate parser."""
        parser = get_parser_for_file(file_path)
        if parser is None:
            raise ValueError(f"No parser available for file: {filename}")

        return parser.parse_bytes(content, filename)

    def _detect_doc_type(self, parsed: ParsedDocument) -> DocType:
        """Auto-detect document type based on content."""
        content = parsed.full_text.lower()

        # Check for API spec indicators
        api_keywords = ["endpoint", "api", "http", "request", "response", "get", "post"]
        api_score = sum(1 for kw in api_keywords if kw in content)

        # Check for table schema indicators
        table_keywords = ["table", "column", "primary key", "foreign key", "schema", "field"]
        table_score = sum(1 for kw in table_keywords if kw in content)

        # Check for system design indicators
        design_keywords = ["architecture", "component", "module", "flow", "diagram", "design"]
        design_score = sum(1 for kw in design_keywords if kw in content)

        # Determine type based on scores
        max_score = max(api_score, table_score, design_score)
        if max_score == 0:
            return DocType.GENERAL
        if api_score == max_score:
            return DocType.API_SPEC
        if table_score == max_score:
            return DocType.TABLE_SCHEMA
        return DocType.SYSTEM_DESIGN

    def _extract_metadata(self, parsed: ParsedDocument) -> DocumentMetadata:
        """Extract metadata from parsed document."""
        api_meta = self.api_extractor.extract(parsed)
        table_meta = self.table_extractor.extract(parsed)
        entity_meta = self.entity_extractor.extract(parsed)

        return DocumentMetadata(
            api_endpoints=api_meta.api_endpoints,
            table_names=table_meta.table_names,
            entity_names=entity_meta.entity_names,
        )

    def _store_chunks(self, chunks: list[Chunk]) -> None:
        """Generate embeddings and store chunks in vector store."""
        if not chunks:
            return

        # Ensure collection exists
        self.vector_store.ensure_collection()

        # Generate embeddings
        contents = [chunk.content for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(contents)

        # Prepare for storage
        ids = [chunk.chunk_id for chunk in chunks]
        payloads = [chunk.to_payload() for chunk in chunks]

        # Store in vector database
        self.vector_store.upsert(ids, embeddings, payloads)

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks."""
        logger.info("Deleting document", document_id=document_id)

        # Delete from vector store
        self.vector_store.delete_by_document_id(document_id)

        # Delete from file storage
        self.file_storage.delete(document_id)

        return True

    def reindex_document(self, document_id: str) -> dict[str, Any]:
        """Reindex an existing document."""
        # Get file from storage
        # This would need to be implemented with proper file tracking
        raise NotImplementedError("Reindexing requires document registry implementation")
