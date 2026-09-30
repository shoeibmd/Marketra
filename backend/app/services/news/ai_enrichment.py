import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import NewsArticle
from app.services.ai.mock import MockAIProvider

logger = logging.getLogger("terminal.news.ai_enrichment")


class AIEnrichmentProcessor:
    """Enriches news articles with structured AI intelligence or sets status to 'pending' if AI is unavailable."""

    def __init__(self) -> None:
        self.ai_provider = MockAIProvider()

    async def enrich_article(self, article: NewsArticle, session: AsyncSession) -> None:
        try:
            analysis = await self.ai_provider.generate_news_analysis(
                title=article.title,
                content=article.content or article.summary,
                company=article.company,
                symbol=article.symbol,
                source=article.source_name,
            )

            article.ai_status = "completed"
            article.ai_importance = analysis.importance_level
            article.ai_impact = analysis.potential_impact
            article.ai_analysis_json = analysis.model_dump()
            session.add(article)

        except Exception as exc:
            logger.warning(f"AI enrichment failed for article {article.id}: {exc}. Setting status to 'pending'.")
            article.ai_status = "pending"
            session.add(article)

    async def process_pending_articles(self, session: AsyncSession, limit: int = 10) -> int:
        stmt = (
            select(NewsArticle)
            .where(NewsArticle.ai_status == "pending")
            .order_by(NewsArticle.published_at.desc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        articles = res.scalars().all()

        processed = 0
        for art in articles:
            await self.enrich_article(art, session)
            processed += 1

        await session.commit()
        return processed
