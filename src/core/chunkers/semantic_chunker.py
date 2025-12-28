"""Semantic chunker that respects sentence boundaries."""

from src.core.chunkers.base import BaseChunker, Chunk
from src.core.parsers.base import ParsedDocument, ContentType


class SemanticChunker(BaseChunker):
    """
    Chunker that splits text at semantic boundaries.

    Respects sentence boundaries and tries to keep related content together.
    """

    # Sentence ending patterns
    SENTENCE_ENDINGS = {"。", "！", "？", ".", "!", "?", "\n\n"}

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        respect_sentences: bool = True,
    ):
        super().__init__(chunk_size, chunk_overlap)
        self.respect_sentences = respect_sentences

    def chunk(
        self,
        document: ParsedDocument,
        document_id: str,
    ) -> list[Chunk]:
        """Split document into semantic chunks."""
        chunks: list[Chunk] = []

        for section in document.sections:
            section_chunks = self._chunk_section(
                content=section.content,
                document_id=document_id,
                content_type=section.content_type,
                section_hierarchy=section.section_hierarchy,
                metadata={
                    "heading_text": section.heading_text,
                    "heading_level": section.heading_level,
                    "code_language": section.code_language,
                    "page_number": section.page_number,
                },
            )
            chunks.extend(section_chunks)

        return chunks

    def _chunk_section(
        self,
        content: str,
        document_id: str,
        content_type: ContentType,
        section_hierarchy: list[str],
        metadata: dict,
    ) -> list[Chunk]:
        """Chunk a single section."""
        # Don't chunk small content
        if self._count_tokens(content) <= self.chunk_size:
            return [
                Chunk.create(
                    document_id=document_id,
                    content=content,
                    content_type=content_type,
                    section_hierarchy=section_hierarchy,
                    metadata={k: v for k, v in metadata.items() if v is not None},
                )
            ]

        # For code blocks and tables, keep them intact if possible
        if content_type in (ContentType.CODE_BLOCK, ContentType.TABLE):
            return [
                Chunk.create(
                    document_id=document_id,
                    content=content,
                    content_type=content_type,
                    section_hierarchy=section_hierarchy,
                    metadata={k: v for k, v in metadata.items() if v is not None},
                )
            ]

        # Split at sentence boundaries
        chunks: list[Chunk] = []
        sentences = self._split_sentences(content)

        current_chunk_sentences: list[str] = []
        current_length = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            # If single sentence exceeds chunk size, split it
            if sentence_tokens > self.chunk_size:
                # Save current chunk first
                if current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences)
                    chunks.append(
                        Chunk.create(
                            document_id=document_id,
                            content=chunk_text,
                            content_type=content_type,
                            section_hierarchy=section_hierarchy,
                            metadata={k: v for k, v in metadata.items() if v is not None},
                        )
                    )
                    current_chunk_sentences = []
                    current_length = 0

                # Split long sentence
                sub_chunks = self._split_long_text(sentence)
                for sub_chunk in sub_chunks:
                    chunks.append(
                        Chunk.create(
                            document_id=document_id,
                            content=sub_chunk,
                            content_type=content_type,
                            section_hierarchy=section_hierarchy,
                            metadata={k: v for k, v in metadata.items() if v is not None},
                        )
                    )
                continue

            # Check if adding sentence exceeds chunk size
            if current_length + sentence_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences)
                    chunks.append(
                        Chunk.create(
                            document_id=document_id,
                            content=chunk_text,
                            content_type=content_type,
                            section_hierarchy=section_hierarchy,
                            metadata={k: v for k, v in metadata.items() if v is not None},
                        )
                    )

                    # Keep overlap
                    overlap_sentences = self._get_overlap_sentences(
                        current_chunk_sentences
                    )
                    current_chunk_sentences = overlap_sentences
                    current_length = sum(
                        self._count_tokens(s) for s in current_chunk_sentences
                    )

            current_chunk_sentences.append(sentence)
            current_length += sentence_tokens

        # Don't forget last chunk
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append(
                Chunk.create(
                    document_id=document_id,
                    content=chunk_text,
                    content_type=content_type,
                    section_hierarchy=section_hierarchy,
                    metadata={k: v for k, v in metadata.items() if v is not None},
                )
            )

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        sentences: list[str] = []
        current = []

        for char in text:
            current.append(char)
            if char in self.SENTENCE_ENDINGS:
                sentence = "".join(current).strip()
                if sentence:
                    sentences.append(sentence)
                current = []

        # Last part
        if current:
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)

        return sentences

    def _split_long_text(self, text: str) -> list[str]:
        """Split text that's too long into smaller pieces."""
        chunks = []
        words = text.split()
        current_words: list[str] = []
        current_length = 0

        for word in words:
            word_tokens = self._count_tokens(word)
            if current_length + word_tokens > self.chunk_size:
                if current_words:
                    chunks.append(" ".join(current_words))
                current_words = [word]
                current_length = word_tokens
            else:
                current_words.append(word)
                current_length += word_tokens

        if current_words:
            chunks.append(" ".join(current_words))

        return chunks

    def _get_overlap_sentences(self, sentences: list[str]) -> list[str]:
        """Get sentences for overlap."""
        if not sentences:
            return []

        overlap_tokens = 0
        overlap_sentences: list[str] = []

        for sentence in reversed(sentences):
            sentence_tokens = self._count_tokens(sentence)
            if overlap_tokens + sentence_tokens <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break

        return overlap_sentences
