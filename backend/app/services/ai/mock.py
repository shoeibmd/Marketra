import math
import uuid

from app.schemas.ai import AIResponse, Citation
from app.services.ai.base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    """Deterministic Mock AI Provider for local dev and unit testing."""

    def __init__(self) -> None:
        super().__init__(model_name="mock-financial-rag-v1")

    async def generate_completion(self, prompt: str, context: str) -> AIResponse:
        cite_id = str(uuid.uuid4())
        return AIResponse(
            answer=(
                f"Based on financial records for '{prompt}': The company maintains strong revenue growth and healthy "
                "free cash flow."
            ),
            citations=[
                Citation(
                    source_type="financial_statement",
                    source_id=cite_id,
                    snippet="Revenue reached $383.28B with operating cash flow of $110.54B.",
                    relevance_score=0.92,
                )
            ],
            confidence=0.95,
            model_used=self.model_name,
            source_facts=["2024 Total Revenue: $383.28B", "Operating Cash Flow: $110.54B"],
            calculated_metrics=["Free Cash Flow Margin: ~26.0%", "P/E Ratio: 28.5x"],
            interpretation=["Strong balance sheet positions company well for market expansion."],
        )

    async def generate_embedding(self, text: str) -> list[float]:
        # Deterministic 128-dim pseudo-embedding vector based on text hash
        hash_val = sum(ord(c) for c in text)
        return [math.sin(hash_val + i) for i in range(128)]
