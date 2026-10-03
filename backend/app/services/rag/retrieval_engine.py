from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import ArticleInstrument, EventCompanyRelationship, FinancialEvent, Instrument, NewsArticle
from uuid import UUID

from app.schemas.ai import ResearchQueryParsed
from app.services.analytics.event_market_analytics import EventMarketAnalyticsService
from app.services.analytics.portfolio_analytics import PortfolioAnalyticsService
from app.services.analytics.portfolio_risk import PortfolioRiskService
from app.services.providers.mock import MockProvider

mock_market_provider = MockProvider()


def sanitize_text(text: str) -> str:
    """Prompt injection protection: Strips instruction hijacking syntax from retrieved news articles."""
    cleaned = text.replace("System:", "").replace("User:", "").replace("Assistant:", "")
    cleaned = cleaned.replace("IGNORE PREVIOUS INSTRUCTIONS", "")
    return cleaned.strip()


class RAGRetrievalEngine:
    """Multi-source evidence retriever querying news, events, company relationships, market data, and historical observations."""

    @staticmethod
    async def retrieve_evidence(
        parsed: ResearchQueryParsed,
        db_session: AsyncSession,
        user_id: UUID | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        start_date = now - timedelta(days=parsed.date_range_days)

        evidence: dict[str, Any] = {
            "parsed_query": parsed.model_dump(),
            "symbol": parsed.symbol,
            "company_name": None,
            "news_articles": [],
            "financial_events": [],
            "relationships": [],
            "historical_analytics": None,
            "market_data": None,
            "evidence_confidence": "HIGH",
        }

        # 1. Instrument / Company Info & Historical Analytics
        inst = None
        if parsed.symbol:
            inst_stmt = select(Instrument).where(Instrument.symbol == parsed.symbol)
            inst_res = await db_session.execute(inst_stmt)
            inst = inst_res.scalar_one_or_none()

            if inst:
                evidence["company_name"] = inst.name
                q = await mock_market_provider.get_realtime_quote(inst)
                prev_close = round(q.last_price * 0.992, 2)
                evidence["market_data"] = {
                    "symbol": inst.symbol,
                    "company_name": inst.name,
                    "currency": inst.currency,
                    "current_price": q.last_price,
                    "previous_close": prev_close,
                    "change_percent": round(((q.last_price - prev_close) / prev_close) * 100, 2),
                    "volume": q.last_size * 1250,
                    "sector": inst.sector or "General Equity",
                }

        # 2. Financial Events Retrieval
        event_stmt = select(FinancialEvent).where(FinancialEvent.event_date >= start_date)

        if parsed.symbol:
            subq = select(EventCompanyRelationship.event_id).join(Instrument).where(Instrument.symbol == parsed.symbol)
            event_stmt = event_stmt.where(or_(FinancialEvent.primary_company_id.in_(select(Instrument.id).where(Instrument.symbol == parsed.symbol)), FinancialEvent.id.in_(subq)))

        if parsed.event_type:
            event_stmt = event_stmt.where(FinancialEvent.event_type == parsed.event_type)

        if parsed.sector:
            event_stmt = event_stmt.where(FinancialEvent.sector.ilike(f"%{parsed.sector}%"))

        event_stmt = event_stmt.order_by(FinancialEvent.event_date.desc()).limit(10)
        event_res = await db_session.execute(event_stmt)
        events = event_res.scalars().all()

        evidence["financial_events"] = [
            {
                "id": str(e.id),
                "type": e.event_type,
                "title": sanitize_text(e.event_title),
                "summary": sanitize_text(e.event_summary),
                "date": e.event_date.isoformat(),
                "importance": e.importance,
                "source": e.source_name,
                "url": e.source_url,
            }
            for e in events
        ]

        # 3. Calculate Historical Event Market Observations
        if inst and events:
            analytics_service = EventMarketAnalyticsService(db_session)
            observations = []
            for e in events:
                obs = await analytics_service.calculate_event_observation(e, inst)
                observations.append(obs)

            stats_1d = EventMarketAnalyticsService.compute_aggregate_statistics(observations, "1d")
            stats_5d = EventMarketAnalyticsService.compute_aggregate_statistics(observations, "5d")

            evidence["historical_analytics"] = {
                "symbol": inst.symbol,
                "observations_count": len(observations),
                "aggregate_statistics_1d": stats_1d,
                "aggregate_statistics_5d": stats_5d,
                "disclaimer": "Historical event observations are factual price measurements and do not state or imply event causation or future stock returns.",
            }

        # 4. News Articles Retrieval
        news_stmt = select(NewsArticle).where(NewsArticle.published_at >= start_date)

        if parsed.symbol:
            subq_news = select(ArticleInstrument.article_id).join(Instrument).where(Instrument.symbol == parsed.symbol)
            news_stmt = news_stmt.where(or_(NewsArticle.symbol == parsed.symbol, NewsArticle.id.in_(subq_news)))

        news_stmt = news_stmt.order_by(NewsArticle.published_at.desc()).limit(10)
        news_res = await db_session.execute(news_stmt)
        articles = news_res.scalars().all()

        evidence["news_articles"] = [
            {
                "id": str(a.id),
                "title": sanitize_text(a.title),
                "summary": sanitize_text(a.summary or a.title),
                "published_at": a.published_at.isoformat(),
                "source": a.source_name,
                "url": a.url,
                "symbol": a.symbol,
            }
            for a in articles
        ]

        # 5. Company Relationships
        if parsed.symbol:
            rel_stmt = (
                select(Instrument.symbol, Instrument.name, EventCompanyRelationship.role, EventCompanyRelationship.relationship_note)
                .join(EventCompanyRelationship)
                .join(FinancialEvent)
                .where(FinancialEvent.primary_company_id == select(Instrument.id).where(Instrument.symbol == parsed.symbol).scalar_subquery(), Instrument.symbol != parsed.symbol)
                .limit(5)
            )
            rel_res = await db_session.execute(rel_stmt)
            evidence["relationships"] = [
                {"symbol": r[0], "name": r[1], "role": r[2], "note": r[3]} for r in rel_res.all()
            ]

        # 6. Portfolio Intelligence & Risk Context (if user_id provided)
        if user_id:
            try:
                portfolio_analytics_svc = PortfolioAnalyticsService(db_session)
                portfolio_analytics = await portfolio_analytics_svc.generate_portfolio_analytics(user_id=user_id)

                portfolio_risk_svc = PortfolioRiskService(db_session)
                var_es = await portfolio_risk_svc.calculate_var_and_es(user_id=user_id)
                div = await portfolio_risk_svc.calculate_diversification_metrics(user_id=user_id)
                corr = await portfolio_risk_svc.calculate_correlation_matrix(user_id=user_id)
                stress_m10 = await portfolio_risk_svc.run_stress_test(
                    user_id=user_id, market_shock_pct=-10.0, scenario_name="NIFTY50_-10%"
                )

                # Filter portfolio evidence if specific symbol is queried
                pos_match = None
                if parsed.symbol and "positions" in portfolio_analytics:
                    for pos in portfolio_analytics["positions"]:
                        if pos.get("symbol") == parsed.symbol:
                            pos_match = pos
                            break

                evidence["portfolio_analytics"] = {
                    "account_summary": portfolio_analytics.get("summary"),
                    "risk_analytics": portfolio_analytics.get("risk_analytics"),
                    "var_and_expected_shortfall": var_es,
                    "diversification": div,
                    "highly_correlated_pairs": corr.get("highly_correlated_pairs", []),
                    "stress_test_nifty_minus_10": stress_m10.get("hypothetical_impact"),
                    "queried_symbol_position": pos_match,
                    "disclaimer": "Portfolio context and risk analytics are factual internal position and statistical risk data.",
                }
            except Exception as e:
                evidence["portfolio_analytics"] = {"status": "UNAVAILABLE", "error": str(e)}

        # Evidence Confidence Assessment
        total_items = len(evidence["financial_events"]) + len(evidence["news_articles"])
        if total_items >= 3:
            evidence["evidence_confidence"] = "HIGH"
        elif total_items >= 1:
            evidence["evidence_confidence"] = "MEDIUM"
        else:
            evidence["evidence_confidence"] = "LOW"

        return evidence
