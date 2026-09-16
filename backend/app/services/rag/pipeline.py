from app.schemas.ai import AIResponse
from app.services.ai.mock import MockAIProvider


class RAGPipeline:
    """Retrieval-Augmented Generation (RAG) Pipeline."""

    def __init__(self) -> None:
        self.ai_provider = MockAIProvider()

    @staticmethod
    def chunk_document(content: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Split document text into overlapping chunks."""
        words = content.split()
        chunks = []
        step = chunk_size - overlap
        for i in range(0, len(words), step):
            chunk_words = words[i : i + chunk_size]
            chunks.append(" ".join(chunk_words))
            if i + chunk_size >= len(words):
                break
        return chunks if chunks else [content]

    async def run_query(self, query: str, instrument_id: str | None = None) -> AIResponse:
        """Run full RAG retrieval + AI generation pipeline."""
        context_str = f"Context for query '{query}' regarding instrument '{instrument_id or 'GLOBAL'}'."
        return await self.ai_provider.generate_completion(query, context_str)


rag_pipeline = RAGPipeline()
