"""Qdrant vector store integration."""

from typing import Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.models import Distance, VectorParams

from src.config import get_settings

settings = get_settings()


class VectorStore:
    """Qdrant vector store wrapper."""

    VECTOR_SIZE = 1024  # bge-large embedding dimension

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
    ):
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name or settings.qdrant_collection
        self._client: Optional[QdrantClient] = None

    @property
    def client(self) -> QdrantClient:
        """Get or create Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(host=self.host, port=self.port)
        return self._client

    def ensure_collection(self) -> None:
        """Ensure the collection exists with proper schema."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

            # Create payload indexes for filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="document_id",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="doc_type",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="tags",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )

    def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        """Upsert vectors with payloads."""
        points = [
            qdrant_models.PointStruct(
                id=idx,
                vector=vector,
                payload=payload,
            )
            for idx, (vector, payload) in enumerate(zip(vectors, payloads))
        ]
        # Use string IDs by creating named vectors
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                qdrant_models.PointStruct(
                    id=i,
                    vector=vectors[i],
                    payload={**payloads[i], "chunk_id": ids[i]},
                )
                for i in range(len(ids))
            ],
        )

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        query_filter = None
        if filters:
            conditions = []
            if "doc_types" in filters and filters["doc_types"]:
                conditions.append(
                    qdrant_models.FieldCondition(
                        key="doc_type",
                        match=qdrant_models.MatchAny(any=filters["doc_types"]),
                    )
                )
            if "tags" in filters and filters["tags"]:
                conditions.append(
                    qdrant_models.FieldCondition(
                        key="tags",
                        match=qdrant_models.MatchAny(any=filters["tags"]),
                    )
                )
            if "document_id" in filters:
                conditions.append(
                    qdrant_models.FieldCondition(
                        key="document_id",
                        match=qdrant_models.MatchValue(value=filters["document_id"]),
                    )
                )
            if conditions:
                query_filter = qdrant_models.Filter(must=conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload,
            }
            for r in results
        ]

    def delete_by_document_id(self, document_id: str) -> None:
        """Delete all vectors for a document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=qdrant_models.FilterSelector(
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="document_id",
                            match=qdrant_models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )

    def get_collection_info(self) -> dict[str, Any]:
        """Get collection statistics."""
        info = self.client.get_collection(self.collection_name)
        return {
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status.value,
        }

    def health_check(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
