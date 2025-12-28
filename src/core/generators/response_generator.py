"""Response generator for RAG Q&A."""

from typing import Any, Optional

from src.core.generators.base import BaseGenerator, GeneratedResponse
from src.core.retrievers.base import RetrievalResult
from src.infrastructure.llm_client import LLMClient, get_llm_client


class ResponseGenerator(BaseGenerator):
    """Generator for producing Q&A responses."""

    # Default system prompt
    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions about system design documents.

Guidelines:
1. Base your answers ONLY on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Cite specific sections or documents when possible
4. Use clear formatting (bullet points, code blocks) for technical content
5. Respond in the same language as the question

When answering:
- Be precise and accurate
- Include relevant technical details
- Mention related concepts if they appear in the context"""

    RESPONSE_MODE_INSTRUCTIONS = {
        "concise": "Provide a brief, focused answer in 2-3 sentences.",
        "detailed": "Provide a comprehensive answer with full explanations and examples.",
        "comparison": "Compare and contrast the relevant information, highlighting differences.",
        "structured": "Structure your answer with clear headings and bullet points.",
    }

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        system_prompt: Optional[str] = None,
    ):
        self.llm_client = llm_client or get_llm_client()
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT

    async def generate(
        self,
        query: str,
        context: list[RetrievalResult],
        **kwargs: Any,
    ) -> GeneratedResponse:
        """Generate a response using the LLM."""
        response_mode = kwargs.get("response_mode", "detailed")
        include_sources = kwargs.get("include_sources", True)

        # Build context string
        context_text = self._build_context(context)

        # Build prompt
        prompt = self._build_prompt(query, context_text, response_mode)

        # Generate response
        content = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
        )

        # Extract sources
        sources = []
        if include_sources:
            sources = self._extract_sources(context)

        # Calculate confidence
        confidence = self._calculate_confidence(context)

        return GeneratedResponse(
            content=content,
            sources=sources,
            confidence=confidence,
            metadata={
                "response_mode": response_mode,
                "context_chunks": len(context),
            },
        )

    def _build_context(self, context: list[RetrievalResult]) -> str:
        """Build context string from retrieval results."""
        if not context:
            return "No relevant context found."

        parts = []
        for i, result in enumerate(context, 1):
            heading = result.metadata.get("heading_text", "")
            filename = result.metadata.get("filename", "")

            header = f"[Context {i}]"
            if filename:
                header += f" File: {filename}"
            if heading:
                header += f" | Section: {heading}"

            parts.append(f"{header}\n{result.content}")

        return "\n\n---\n\n".join(parts)

    def _build_prompt(
        self,
        query: str,
        context: str,
        response_mode: str,
    ) -> str:
        """Build the generation prompt."""
        mode_instruction = self.RESPONSE_MODE_INSTRUCTIONS.get(
            response_mode,
            self.RESPONSE_MODE_INSTRUCTIONS["detailed"],
        )

        return f"""Based on the following context from system documentation:

{context}

---

Question: {query}

Instructions: {mode_instruction}

Please provide your answer:"""

    def _extract_sources(self, context: list[RetrievalResult]) -> list[dict[str, Any]]:
        """Extract source references from context."""
        sources = []
        seen_docs = set()

        for result in context:
            doc_id = result.document_id
            if doc_id in seen_docs:
                continue
            seen_docs.add(doc_id)

            sources.append({
                "document_id": doc_id,
                "filename": result.metadata.get("filename", ""),
                "section": result.metadata.get("heading_text"),
                "score": result.score,
            })

        return sources

    def _calculate_confidence(self, context: list[RetrievalResult]) -> float:
        """Calculate confidence score based on context quality."""
        if not context:
            return 0.0

        # Average of top scores
        scores = [r.score for r in context[:3]]
        avg_score = sum(scores) / len(scores)

        # Boost if we have multiple high-quality results
        high_quality_count = sum(1 for r in context if r.score > 0.7)
        boost = min(high_quality_count * 0.05, 0.15)

        confidence = min(avg_score + boost, 1.0)
        return round(confidence, 2)

    async def generate_with_fallback(
        self,
        query: str,
        context: list[RetrievalResult],
        **kwargs: Any,
    ) -> GeneratedResponse:
        """Generate with fallback message if context is insufficient."""
        if not context or all(r.score < 0.5 for r in context):
            return GeneratedResponse(
                content="I couldn't find sufficient information in the documentation to answer your question. "
                "Please try rephrasing your question or ensure the relevant documents are indexed.",
                sources=[],
                confidence=0.0,
                metadata={"fallback": True},
            )

        return await self.generate(query, context, **kwargs)
