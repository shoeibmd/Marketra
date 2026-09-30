import asyncio
import logging
import uuid
from typing import Any

from celery import Celery
from sqlalchemy import select

from app.api.websockets import manager as ws_manager
from app.core.config import settings
from app.db.session import PostgresSessionLocal
from app.models.domain import ArticleInstrument, EventCompanyRelationship, FinancialEvent, Instrument, NewsArticle
from app.services.ai.mock import MockAIProvider
from app.services.news.ai_enrichment import AIEnrichmentProcessor
from app.services.news.matcher import CompanyMatcher
from app.services.news.rss import RSSNewsProvider

logger = logging.getLogger("terminal.celery.tasks")

celery_app = Celery(
    "terminal_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_live_news_feeds(self: Any) -> dict[str, int]:
    """Celery background worker task for ingesting live Indian market news feeds, extracting events, and broadcasting alerts."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        inserted_count, skipped_count = loop.run_until_complete(_ingest_news_async())
        logger.info(f"News sync complete: {inserted_count} inserted, {skipped_count} duplicates skipped.")
        return {"inserted": inserted_count, "skipped": skipped_count}
    except Exception as exc:
        logger.error(f"Error executing news feed sync: {exc}")
        raise self.retry(exc=exc)


async def _ingest_news_async() -> tuple[int, int]:
    provider = RSSNewsProvider()
    ai_processor = AIEnrichmentProcessor()
    mock_ai = MockAIProvider()
    items = await provider.fetch_news()

    inserted = 0
    skipped = 0

    async with PostgresSessionLocal() as session:
        for item in items:
            # Safe duplicate check via content_hash or URL
            stmt = select(NewsArticle).where(
                (NewsArticle.content_hash == item.content_hash) | (NewsArticle.url == item.original_url)
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if existing:
                skipped += 1
                continue

            # Multi-company entity matching
            matches = await CompanyMatcher.match_instruments(
                title=item.title,
                content=item.summary or item.content,
                db_session=session,
                hint_symbol=item.symbol,
            )

            primary_inst_id = matches[0][0] if matches else None

            article = NewsArticle(
                id=item.id,
                instrument_id=primary_inst_id,
                title=item.title,
                summary=item.summary,
                content=item.content,
                source_name=item.source_name,
                source_url=item.source_url,
                url=item.original_url,
                published_at=item.published_at,
                discovered_at=item.discovered_at,
                company=item.company,
                symbol=item.symbol,
                exchange=item.exchange,
                category=item.category,
                raw_metadata=item.raw_metadata,
                content_hash=item.content_hash,
                processing_status="normalized",
            )

            # AI Analysis enrichment
            await ai_processor.enrich_article(article, session)
            session.add(article)

            for inst_id, sym, sector, score in matches:
                junction = ArticleInstrument(
                    article_id=article.id,
                    instrument_id=inst_id,
                    relevance_score=score,
                    sector=sector,
                )
                session.add(junction)

            # Phase 10: Extract Financial Event
            extracted_event = await mock_ai.extract_financial_event(
                title=article.title,
                content=article.content or article.summary,
                company=article.company,
                symbol=article.symbol,
            )

            fin_event = FinancialEvent(
                id=uuid.uuid4(),
                news_id=article.id,
                cluster_id=extracted_event.cluster_id,
                event_type=extracted_event.event_type,
                event_title=extracted_event.event_title,
                event_summary=extracted_event.event_summary,
                event_date=article.published_at,
                primary_company_id=primary_inst_id,
                sector=extracted_event.sector,
                importance=extracted_event.importance,
                confidence=extracted_event.confidence,
                source_name=article.source_name,
                source_url=article.url,
                verified_facts={"facts": extracted_event.verified_facts},
                ai_analysis_json={"analysis": extracted_event.ai_analysis_text},
                potential_impact=extracted_event.potential_impact,
                uncertainties={"uncertainties": extracted_event.uncertainties},
            )
            session.add(fin_event)

            for inst_id, sym, sector, score in matches:
                rel = EventCompanyRelationship(
                    event_id=fin_event.id,
                    instrument_id=inst_id,
                    role="PRIMARY_SUBJECT" if inst_id == primary_inst_id else "PARTNER",
                    relationship_note=f"Co-mentioned entity with relevance score {score}",
                )
                session.add(rel)

            inserted += 1

            # Broadcast WebSocket news_alert and financial_event
            if article.ai_importance in ["HIGH", "CRITICAL"] or article.category in ["corporate_earnings", "regulation"]:
                alert_payload = {
                    "news_id": str(article.id),
                    "symbol": article.symbol or (matches[0][1] if matches else "INDIA_MARKET"),
                    "company": article.company or "Indian Listed Entity",
                    "title": article.title,
                    "category": article.category,
                    "importance": article.ai_importance or "HIGH",
                    "summary": article.summary or article.title,
                    "published_at": article.published_at.isoformat(),
                }
                await ws_manager.broadcast_news_alert(alert_payload)

                event_payload = {
                    "event_id": str(fin_event.id),
                    "event_type": fin_event.event_type,
                    "company": article.company or "Indian Listed Entity",
                    "related_companies": [m[1] for m in matches[1:]],
                    "importance": fin_event.importance,
                    "summary": fin_event.event_summary,
                    "published_at": fin_event.event_date.isoformat(),
                }
                await ws_manager.broadcast_financial_event(event_payload)

        await session.commit()

    return inserted, skipped
