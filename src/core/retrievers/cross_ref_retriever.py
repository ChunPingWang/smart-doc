"""Cross-reference retriever for finding related documents."""

from typing import Any, Optional

from src.core.retrievers.base import BaseRetriever, RetrievalResult
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.embedding import EmbeddingService


class CrossRefRetriever(BaseRetriever):
    """
    Retriever that finds cross-referenced documents.

    When querying about an API, automatically includes related table schemas.
    When querying about a table, includes related API endpoints.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        max_cross_refs: int = 3,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService()
        self.max_cross_refs = max_cross_refs

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Retrieve with cross-references."""
        # First, get primary results
        primary_results = self._primary_retrieve(query, top_k, filters)

        # Then, find cross-references
        cross_refs = self._find_cross_references(primary_results)

        # Combine, with primary results first
        combined = primary_results + cross_refs

        # Deduplicate
        seen = set()
        unique_results = []
        for result in combined:
            if result.chunk_id not in seen:
                seen.add(result.chunk_id)
                unique_results.append(result)

        return unique_results

    async def aretrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Async cross-reference retrieval."""
        return self.retrieve(query, top_k, filters)

    def _primary_retrieve(
        self,
        query: str,
        top_k: int,
        filters: Optional[dict[str, Any]],
    ) -> list[RetrievalResult]:
        """Perform primary retrieval."""
        query_embedding = self.embedding_service.embed_query(query)

        results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            filters=filters,
        )

        return [
            RetrievalResult(
                chunk_id=r["payload"].get("chunk_id", ""),
                document_id=r["payload"].get("document_id", ""),
                content=r["payload"].get("content", ""),
                score=r["score"],
                metadata={
                    k: v
                    for k, v in r["payload"].items()
                    if k not in ("chunk_id", "document_id", "content")
                },
                source="primary",
            )
            for r in results
        ]

    def _find_cross_references(
        self,
        primary_results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """Find cross-referenced documents based on primary results."""
        cross_refs: list[RetrievalResult] = []

        for result in primary_results:
            doc_type = result.metadata.get("doc_type", "")

            # If this is an API spec, look for related table schemas
            if doc_type == "api_spec":
                entity_names = result.metadata.get("entity_names", [])
                table_names = result.metadata.get("table_names", [])

                # Search for related table schemas
                related = self._search_related(
                    entities=entity_names + table_names,
                    doc_type="table_schema",
                    exclude_doc_id=result.document_id,
                )
                cross_refs.extend(related[: self.max_cross_refs])

            # If this is a table schema, look for related API specs
            elif doc_type == "table_schema":
                table_names = result.metadata.get("table_names", [])
                entity_names = result.metadata.get("entity_names", [])

                related = self._search_related(
                    entities=table_names + entity_names,
                    doc_type="api_spec",
                    exclude_doc_id=result.document_id,
                )
                cross_refs.extend(related[: self.max_cross_refs])

        return cross_refs

    def _search_related(
        self,
        entities: list[str],
        doc_type: str,
        exclude_doc_id: str,
    ) -> list[RetrievalResult]:
        """Search for documents related to given entities."""
        if not entities:
            return []

        # Create a query from entity names
        query = " ".join(entities)
        query_embedding = self.embedding_service.embed_query(query)

        # Search with doc_type filter
        results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=self.max_cross_refs + 1,  # +1 to account for possible exclusion
            filters={"doc_types": [doc_type]},
        )

        # Filter out the source document and convert to results
        cross_refs = []
        for r in results:
            if r["payload"].get("document_id") == exclude_doc_id:
                continue

            cross_refs.append(
                RetrievalResult(
                    chunk_id=r["payload"].get("chunk_id", ""),
                    document_id=r["payload"].get("document_id", ""),
                    content=r["payload"].get("content", ""),
                    score=r["score"] * 0.8,  # Slightly lower score for cross-refs
                    metadata={
                        k: v
                        for k, v in r["payload"].items()
                        if k not in ("chunk_id", "document_id", "content")
                    },
                    source="cross_reference",
                )
            )

        return cross_refs
