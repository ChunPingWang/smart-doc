"""Embedding service using HuggingFace models."""

from typing import Optional

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Embedding service wrapper for BGE models."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self._embed_model: Optional[HuggingFaceEmbedding] = None

    @property
    def embed_model(self) -> HuggingFaceEmbedding:
        """Get or create embedding model."""
        if self._embed_model is None:
            self._embed_model = HuggingFaceEmbedding(
                model_name=self.model_name,
                trust_remote_code=True,
            )
        return self._embed_model

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string."""
        return self.embed_model.get_text_embedding(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings."""
        return [self.embed_model.get_text_embedding(t) for t in texts]

    def embed_query(self, query: str) -> list[float]:
        """Embed a query string (may use different prefix for BGE models)."""
        return self.embed_model.get_query_embedding(query)

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        # BGE-large models have 1024 dimensions
        return 1024

    def health_check(self) -> bool:
        """Check if embedding model is loaded."""
        try:
            # Try to embed a test string
            _ = self.embed_text("test")
            return True
        except Exception:
            return False


class RerankerService:
    """Reranker service for search result reordering."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.reranker_model
        self._reranker = None

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: Optional[int] = None,
    ) -> list[tuple[int, float]]:
        """
        Rerank documents based on query relevance.

        Returns list of (original_index, score) tuples sorted by score.
        """
        # Lazy import to avoid loading model unless needed
        from llama_index.postprocessor.flag_embedding_reranker import (
            FlagEmbeddingReranker,
        )

        if self._reranker is None:
            self._reranker = FlagEmbeddingReranker(
                model=self.model_name,
                top_n=top_k or len(documents),
            )

        # For now, return original order with dummy scores
        # TODO: Implement actual reranking
        return [(i, 1.0 - i * 0.1) for i in range(len(documents))]
