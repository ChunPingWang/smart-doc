"""Hybrid retriever combining dense and sparse search."""

from typing import Any, Optional

from src.core.retrievers.base import BaseRetriever, RetrievalResult
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.embedding import EmbeddingService


class HybridRetriever(BaseRetriever):
    """
    Hybrid retriever that combines dense (semantic) and sparse (keyword) search.

    Uses reciprocal rank fusion (RRF) to combine results.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        rrf_k: int = 60,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService()
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.rrf_k = rrf_k

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Retrieve using hybrid search."""
        # Dense retrieval
        dense_results = self._dense_retrieve(query, top_k * 2, filters)

        # Sparse retrieval (keyword matching)
        # Note: Qdrant supports sparse vectors, but for simplicity,
        # we'll use text matching on the payload for now
        sparse_results = self._sparse_retrieve(query, top_k * 2, filters)

        # Combine using RRF
        combined = self._reciprocal_rank_fusion(dense_results, sparse_results)

        return combined[:top_k]

    async def aretrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Async hybrid retrieval."""
        # For now, just wrap sync version
        return self.retrieve(query, top_k, filters)

    def _dense_retrieve(
        self,
        query: str,
        top_k: int,
        filters: Optional[dict[str, Any]],
    ) -> list[RetrievalResult]:
        """Perform dense (semantic) retrieval."""
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
                source="dense",
            )
            for r in results
        ]

    def _sparse_retrieve(
        self,
        query: str,
        top_k: int,
        filters: Optional[dict[str, Any]],
    ) -> list[RetrievalResult]:
        """
        Perform sparse (keyword) retrieval.

        Note: This is a simplified implementation. For production,
        consider using BM25 or Qdrant's sparse vector support.
        """
        # For now, return empty list - proper sparse search would need
        # a keyword index or BM25 implementation
        return []

    def _reciprocal_rank_fusion(
        self,
        dense_results: list[RetrievalResult],
        sparse_results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """
        Combine results using Reciprocal Rank Fusion (RRF).

        RRF score = sum(1 / (k + rank)) for each result list
        """
        # Build score map
        scores: dict[str, float] = {}
        result_map: dict[str, RetrievalResult] = {}

        # Process dense results
        for rank, result in enumerate(dense_results):
            chunk_id = result.chunk_id
            rrf_score = self.dense_weight / (self.rrf_k + rank + 1)
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            result_map[chunk_id] = result

        # Process sparse results
        for rank, result in enumerate(sparse_results):
            chunk_id = result.chunk_id
            rrf_score = self.sparse_weight / (self.rrf_k + rank + 1)
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in result_map:
                result_map[chunk_id] = result

        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        # Build final results
        combined = []
        for chunk_id in sorted_ids:
            result = result_map[chunk_id]
            combined.append(
                RetrievalResult(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    content=result.content,
                    score=scores[chunk_id],
                    metadata=result.metadata,
                    source="hybrid",
                )
            )

        return combined
