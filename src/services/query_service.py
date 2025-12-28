"""Query service for search and Q&A."""

from typing import Any, Optional

import structlog

from src.api.schemas import (
    QueryFilters,
    ResponseMode,
    SearchResult,
    CrossReference,
    SourceReference,
)
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.embedding import EmbeddingService
from src.infrastructure.llm_client import LLMClient, get_llm_client

logger = structlog.get_logger()


class QueryService:
    """Service for document search and question answering."""

    # System prompt for Q&A
    QA_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on system design documents.
Use the provided context to answer questions accurately.
Always cite your sources by mentioning the document name or section.
If you cannot find relevant information in the context, say so clearly.
Respond in the same language as the question."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService()
        self.llm_client = llm_client or get_llm_client()

    def search(
        self,
        query: str,
        filters: Optional[QueryFilters] = None,
        top_k: int = 5,
        include_cross_reference: bool = True,
    ) -> list[SearchResult]:
        """
        Search for relevant document chunks.

        Args:
            query: Search query
            filters: Optional filters (doc_types, tags, etc.)
            top_k: Number of results to return
            include_cross_reference: Whether to include cross-references

        Returns:
            List of search results with scores
        """
        logger.info("Searching documents", query=query, top_k=top_k)

        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Build filter dict
        filter_dict = self._build_filters(filters)

        # Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            filters=filter_dict,
        )

        # Convert to SearchResult objects
        search_results = []
        for result in results:
            payload = result.get("payload", {})

            cross_refs = []
            if include_cross_reference:
                cross_refs = self._find_cross_references(payload)

            search_results.append(
                SearchResult(
                    chunk_id=payload.get("chunk_id", ""),
                    document_id=payload.get("document_id", ""),
                    content=payload.get("content", ""),
                    score=result.get("score", 0.0),
                    metadata={
                        k: v
                        for k, v in payload.items()
                        if k not in ("chunk_id", "document_id", "content")
                    },
                    cross_references=cross_refs,
                )
            )

        return search_results

    async def ask(
        self,
        question: str,
        response_mode: ResponseMode = ResponseMode.DETAILED,
        include_sources: bool = True,
        filters: Optional[QueryFilters] = None,
    ) -> dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: The question to answer
            response_mode: How detailed the response should be
            include_sources: Whether to include source references
            filters: Optional filters for retrieval

        Returns:
            Answer with sources and confidence score
        """
        logger.info("Answering question", question=question, mode=response_mode)

        # Search for relevant context
        search_results = self.search(
            query=question,
            filters=filters,
            top_k=5,
            include_cross_reference=True,
        )

        if not search_results:
            return {
                "answer": "I couldn't find relevant information to answer your question.",
                "sources": [],
                "confidence": 0.0,
            }

        # Build context from search results
        context = self._build_context(search_results, response_mode)

        # Generate answer using LLM
        prompt = self._build_qa_prompt(question, context, response_mode)
        answer = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=self.QA_SYSTEM_PROMPT,
        )

        # Extract sources
        sources = []
        if include_sources:
            sources = self._extract_sources(search_results)

        # Calculate confidence based on search scores
        confidence = self._calculate_confidence(search_results)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        }

    def _build_filters(self, filters: Optional[QueryFilters]) -> Optional[dict]:
        """Convert QueryFilters to vector store filter format."""
        if filters is None:
            return None

        filter_dict = {}
        if filters.doc_types:
            filter_dict["doc_types"] = filters.doc_types
        if filters.tags:
            filter_dict["tags"] = filters.tags

        return filter_dict if filter_dict else None

    def _find_cross_references(self, payload: dict) -> list[CrossReference]:
        """Find cross-references for a chunk."""
        cross_refs = []

        # Look for related entities
        entity_names = payload.get("entity_names", [])
        table_names = payload.get("table_names", [])
        api_endpoints = payload.get("api_endpoints", [])

        # If this is an API doc, find related table schemas
        if api_endpoints and table_names:
            for table in table_names:
                cross_refs.append(
                    CrossReference(
                        chunk_id="",  # Would need additional search
                        document_id="",
                        type="table_schema",
                        table_name=table,
                        relevance="high",
                    )
                )

        return cross_refs

    def _build_context(
        self,
        results: list[SearchResult],
        mode: ResponseMode,
    ) -> str:
        """Build context string from search results."""
        context_parts = []

        for i, result in enumerate(results):
            section = result.metadata.get("heading_text", "")
            doc_id = result.document_id

            header = f"[Source {i + 1}]"
            if section:
                header += f" Section: {section}"

            context_parts.append(f"{header}\n{result.content}")

        return "\n\n---\n\n".join(context_parts)

    def _build_qa_prompt(
        self,
        question: str,
        context: str,
        mode: ResponseMode,
    ) -> str:
        """Build the prompt for Q&A."""
        mode_instructions = {
            ResponseMode.CONCISE: "Provide a brief, concise answer in 2-3 sentences.",
            ResponseMode.DETAILED: "Provide a detailed answer with explanations.",
            ResponseMode.COMPARISON: "Compare and contrast the relevant information.",
        }

        instruction = mode_instructions.get(mode, mode_instructions[ResponseMode.DETAILED])

        return f"""Context from documentation:

{context}

---

Question: {question}

Instructions: {instruction}

Answer:"""

    def _extract_sources(self, results: list[SearchResult]) -> list[SourceReference]:
        """Extract source references from search results."""
        sources = []
        seen = set()

        for result in results:
            doc_id = result.document_id
            if doc_id in seen:
                continue
            seen.add(doc_id)

            sources.append(
                SourceReference(
                    document_id=doc_id,
                    filename=result.metadata.get("filename", ""),
                    section=result.metadata.get("heading_text"),
                )
            )

        return sources

    def _calculate_confidence(self, results: list[SearchResult]) -> float:
        """Calculate confidence score based on search results."""
        if not results:
            return 0.0

        # Use average of top 3 scores
        top_scores = [r.score for r in results[:3]]
        avg_score = sum(top_scores) / len(top_scores)

        # Normalize to 0-1 range (cosine similarity is already in this range)
        return min(max(avg_score, 0.0), 1.0)
