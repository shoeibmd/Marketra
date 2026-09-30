import asyncio
import logging
import uuid
from typing import Any

from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import PostgresSessionLocal
from app.models.domain import Instrument, NewsArticle
from app.services.news.rss import RSSNewsProvider

logger = logging.getLogger("terminal.celery.tasks")

celery_app = Celery(
    "terminal_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_live_news_feeds(self: Any) -> dict[str, int]:
    """Celery background worker task for ingesting live Indian market news feeds."""
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

            inst_id = None
            if item.symbol:
                inst_stmt = select(Instrument).where(Instrument.symbol == item.symbol)
                inst_res = await session.execute(inst_stmt)
                inst = inst_res.scalar_one_or_none()
                if inst:
                    inst_id = inst.id

            article = NewsArticle(
                id=item.id,
                instrument_id=inst_id,
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
            session.add(article)
            inserted += 1

        await session.commit()

    return inserted, skipped
