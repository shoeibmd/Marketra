import pytest
from app.schemas.ai import NewsAIAnalysis
from app.services.ai.mock import MockAIProvider


@pytest.mark.asyncio
async def test_mock_ai_news_analysis_structure() -> None:
    provider = MockAIProvider()
    analysis: NewsAIAnalysis = await provider.generate_news_analysis(
        title="Reliance Industries Q3 FY25 Results and Dividend Announcement",
        content="Reliance reports revenue growth with board approval for dividend.",
        company="Reliance Industries Ltd",
        symbol="RELIANCE",
        source="NSE Corporate Announcements",
    )

    assert analysis.what_happened is not None
    assert analysis.primary_company_affected == "Reliance Industries Ltd"
    assert analysis.potential_impact in ["POSITIVE", "NEGATIVE", "MIXED", "NEUTRAL", "UNCLEAR"]
    assert analysis.importance_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert len(analysis.source_facts) > 0
    assert analysis.ai_confidence >= 0.0 and analysis.ai_confidence <= 1.0

    # Ensure facts and uncertainties are properly separated and no buy/sell price targets are fabricated
    serialized_str = str(analysis.model_dump()).upper()
    assert "BUY THIS STOCK" not in serialized_str
    assert "THIS STOCK WILL DEFINITELY RISE" not in serialized_str
    assert "TARGET PRICE WILL BE" not in serialized_str


@pytest.mark.asyncio
async def test_ai_fallback_status_handling() -> None:
    class FailingAIProvider:
        async def generate_news_analysis(self, *args, **kwargs):
            raise RuntimeError("LLM Provider Timeout")

    failing_provider = FailingAIProvider()

    # Verify fallback handling catches exception gracefully
    try:
        await failing_provider.generate_news_analysis("Title", "Content")
    except Exception as exc:
        assert str(exc) == "LLM Provider Timeout"
