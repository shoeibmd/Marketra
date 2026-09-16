import pytest

from app.services.ai.mock import MockAIProvider
from app.services.rag.pipeline import RAGPipeline


@pytest.mark.asyncio
async def test_mock_ai_provider_completion() -> None:
    provider = MockAIProvider()
    res = await provider.generate_completion("What is AAPL revenue?", "Sample financial context")

    assert res.confidence == 0.95
    assert len(res.citations) == 1
    assert res.citations[0].source_type == "financial_statement"
    assert len(res.source_facts) > 0
    assert len(res.calculated_metrics) > 0
    assert len(res.interpretation) > 0


@pytest.mark.asyncio
async def test_mock_ai_provider_embedding() -> None:
    provider = MockAIProvider()
    embedding = await provider.generate_embedding("Apple Inc 10-K filing")
    assert len(embedding) == 128
    assert all(isinstance(v, float) for v in embedding)


def test_rag_document_chunking() -> None:
    text = "Word " * 1200
    chunks = RAGPipeline.chunk_document(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 2
