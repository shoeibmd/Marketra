import math
import uuid

from app.schemas.ai import AIResponse, Citation, NewsAIAnalysis
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

    async def generate_news_analysis(
        self,
        title: str,
        content: str | None,
        company: str | None = None,
        symbol: str | None = None,
        source: str | None = None,
    ) -> NewsAIAnalysis:
        comp_name = company or symbol or "Indian Listed Entity"
        src_name = source or "Official Exchange Announcement"

        # Determine deterministic impact and importance
        is_critical = "RESULTS" in title.upper() or "EARNINGS" in title.upper() or "POLICY" in title.upper()
        importance = "HIGH" if is_critical else "MEDIUM"
        impact = "POSITIVE" if "DIVIDEND" in title.upper() or "EXPANSION" in title.upper() else "NEUTRAL"

        return NewsAIAnalysis(
            what_happened=f"Official disclosure reported: '{title}'.",
            primary_company_affected=comp_name,
            related_companies=[f"Peer entities in {comp_name} sector"],
            event_category="Corporate Action / Financial Disclosure",
            importance_reason=f"Event introduces fundamental developments for {comp_name} reported by {src_name}.",
            source_facts=[
                f"Source: {src_name}",
                f"Headline: {title}",
                f"Content snippet: {(content or title)[:150]}",
            ],
            potential_impact=impact,  # type: ignore[arg-type]
            importance_level=importance,  # type: ignore[arg-type]
            ai_confidence=0.92,
            user_monitoring_checklist=[
                "Monitor upcoming official regulatory filings on NSE/BSE.",
                "Track segment revenue disclosures and board resolution outcomes.",
            ],
            related_sector="General Equity / Market Index",
            related_announcements=[
                f"Previous quarterly disclosure for {comp_name}",
            ],
            uncertainties_or_gaps=[
                "NOT AVAILABLE FROM SOURCE: Specific long-term financial guidance was not disclosed in the press release."
            ],
            model_used=self.model_name,
        )

    async def generate_embedding(self, text: str) -> list[float]:
        # Deterministic 128-dim pseudo-embedding vector based on text hash
        hash_val = sum(ord(c) for c in text)
        return [math.sin(hash_val + i) for i in range(128)]
