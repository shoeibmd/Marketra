import hashlib
import math
import uuid
from typing import Any

from app.schemas.ai import (
    AIResponse,
    Citation,
    CompanyRoleMapping,
    NewsAIAnalysis,
    ResearchSessionContext,
    SourceGroundedAnswer,
    StructuredFinancialEvent,
)
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

    async def extract_financial_event(
        self,
        title: str,
        content: str | None,
        company: str | None = None,
        symbol: str | None = None,
    ) -> StructuredFinancialEvent:
        comp_name = company or symbol or "Reliance Industries Ltd"
        sym = symbol or "RELIANCE"

        t_upper = title.upper()
        event_type = "OTHER"
        if "RESULTS" in t_upper or "EARNINGS" in t_upper:
            event_type = "RESULTS"
        elif "ACQUISITION" in t_upper or "BUY" in t_upper:
            event_type = "ACQUISITION"
        elif "DIVIDEND" in t_upper:
            event_type = "DIVIDEND"
        elif "PARTNERSHIP" in t_upper or "CONTRACT" in t_upper:
            event_type = "PARTNERSHIP"
        elif "REGULATORY" in t_upper or "FRAMEWORK" in t_upper:
            event_type = "REGULATORY_ACTION"

        cluster_hash = hashlib.sha256(f"{event_type}|{sym}".encode("utf-8")).hexdigest()[:16]

        roles = [
            CompanyRoleMapping(
                company_name=comp_name,
                symbol=sym,
                role="PRIMARY_SUBJECT",
                relationship_note="Primary reporting entity",
            )
        ]

        return StructuredFinancialEvent(
            event_type=event_type,  # type: ignore[arg-type]
            event_title=title,
            event_summary=content or title,
            primary_company=comp_name,
            primary_symbol=sym,
            company_roles=roles,
            sector="Conglomerate / Energy" if sym == "RELIANCE" else "Information Technology",
            importance="HIGH" if event_type in ["RESULTS", "ACQUISITION"] else "MEDIUM",
            confidence=0.92,
            verified_facts=[f"Official filing title: {title}"],
            ai_analysis_text=f"Corporate event '{event_type}' detected for {comp_name} ({sym}).",
            potential_impact="POSITIVE" if event_type == "DIVIDEND" else "NEUTRAL",
            uncertainties=["NOT AVAILABLE FROM SOURCE: Specific future guidance omitted."],
            cluster_id=f"cluster_{cluster_hash}",
        )

    async def generate_source_grounded_research(
        self,
        query: str,
        evidence: dict[str, Any],
    ) -> SourceGroundedAnswer:
        parsed_q = evidence.get("parsed_query", {})
        sym = evidence.get("symbol") or "RELIANCE"
        comp_name = evidence.get("company_name") or "Reliance Industries Ltd"
        events = evidence.get("financial_events", [])
        news = evidence.get("news_articles", [])
        market_ctx = evidence.get("market_data")

        if not events and not news:
            return SourceGroundedAnswer(
                answer_summary=f"Insufficient information available in current database records for query '{query}'.",
                key_facts=["No indexed official disclosures match the specified query range."],
                recent_events=[],
                ai_analysis="Platform retrieval returned 0 matching records.",
                potential_impact="UNCLEAR",
                uncertainties=["NOT AVAILABLE FROM SOURCE: No records retrieved."],
                sources=[],
                related_companies=[],
                market_context=market_ctx,
                evidence_confidence="LOW",
                context_used=ResearchSessionContext(
                    company=comp_name,
                    symbol=sym,
                    sector=parsed_q.get("sector"),
                    event_type=parsed_q.get("event_type"),
                    date_range=f"{parsed_q.get('date_range_days', 30)} days",
                    last_query=query,
                ),
            )

        key_facts = [
            f"Retrieved {len(events)} structured events and {len(news)} news articles.",
            f"Primary subject identified: {comp_name} ({sym}).",
        ]
        for e in events[:3]:
            key_facts.append(f"Event Fact: {e['title']} ({e['date'][:10]})")

        sources_list = [
            {"id": e["id"], "type": "financial_event", "title": e["title"], "source": e["source"], "url": e["url"]}
            for e in events[:3]
        ] + [
            {"id": n["id"], "type": "news_article", "title": n["title"], "source": n["source"], "url": n["url"]}
            for n in news[:3]
        ]

        return SourceGroundedAnswer(
            answer_summary=f"Research synthesis for {comp_name} ({sym}): Disclosures highlight active corporate developments and official announcements.",
            key_facts=key_facts,
            recent_events=events[:5],
            ai_analysis=f"Evidence indicates ongoing strategic operations for {comp_name} across the specified timeframe.",
            potential_impact="POSITIVE" if any("DIVIDEND" in e["title"].upper() for e in events) else "NEUTRAL",
            uncertainties=[
                "NOT AVAILABLE FROM SOURCE: Long-term multi-year guidance was not specified in press statements."
            ],
            sources=sources_list,
            related_companies=[{"symbol": r["symbol"], "name": r["name"], "role": r["role"]} for r in evidence.get("relationships", [])],
            market_context=market_ctx,
            evidence_confidence=evidence.get("evidence_confidence", "HIGH"),
            context_used=ResearchSessionContext(
                company=comp_name,
                symbol=sym,
                sector=parsed_q.get("sector"),
                event_type=parsed_q.get("event_type"),
                date_range=f"{parsed_q.get('date_range_days', 30)} days",
                last_query=query,
            ),
        )

    async def generate_embedding(self, text: str) -> list[float]:
        # Deterministic 128-dim pseudo-embedding vector based on text hash
        hash_val = sum(ord(c) for c in text)
        return [math.sin(hash_val + i) for i in range(128)]
