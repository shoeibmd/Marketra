from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import NewsArticle, User
from app.schemas.market_data import NormalizedNewsArticle
from app.services.news.rss import RSSNewsProvider

router = APIRouter(prefix="/news", tags=["News"])
rss_provider = RSSNewsProvider()


@router.get("", response_model=list[dict[str, Any]])
async def get_news_articles(
    symbol: str | None = Query(None, description="Filter news by instrument symbol"),
    category: str | None = Query(None, description="Filter news by category (e.g. monetary_policy, corporate_earnings)"),
    exchange: str | None = Query(None, description="Filter news by exchange (NSE, BSE)"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Fetch live Indian market news articles from database with optional filters."""
    query = select(NewsArticle)

    if symbol:
        query = query.where(NewsArticle.symbol == symbol.upper().strip())
    if category:
        query = query.where(NewsArticle.category == category.lower().strip())
    if exchange:
        query = query.where(NewsArticle.exchange == exchange.upper().strip())

    query = query.order_by(NewsArticle.published_at.desc()).limit(limit)
    res = await db.execute(query)
    articles = res.scalars().all()

    if articles:
        return [
            {
                "id": str(a.id),
                "title": a.title,
                "summary": a.summary,
                "content": a.content,
                "source_name": a.source_name,
                "source_url": a.source_url,
                "url": a.url,
                "published_at": a.published_at.isoformat(),
                "discovered_at": a.discovered_at.isoformat(),
                "company": a.company,
                "symbol": a.symbol,
                "exchange": a.exchange,
                "category": a.category,
                "content_hash": a.content_hash,
                "processing_status": a.processing_status,
            }
            for a in articles
        ]

    # Fallback to provider sample items if DB is empty
    live_items = await rss_provider.fetch_news()
    filtered = live_items
    if symbol:
        filtered = [i for i in filtered if i.symbol == symbol.upper().strip()]
    if category:
        filtered = [i for i in filtered if i.category == category.lower().strip()]
    if exchange:
        filtered = [i for i in filtered if i.exchange == exchange.upper().strip()]

    return [
        {
            "id": str(i.id),
            "title": i.title,
            "summary": i.summary,
            "content": i.content,
            "source_name": i.source_name,
            "source_url": i.source_url,
            "url": i.original_url,
            "published_at": i.published_at.isoformat(),
            "discovered_at": i.discovered_at.isoformat(),
            "company": i.company,
            "symbol": i.symbol,
            "exchange": i.exchange,
            "category": i.category,
            "content_hash": i.content_hash,
            "processing_status": i.processing_status,
        }
        for i in filtered[:limit]
    ]


@router.get("/{article_id}", response_model=dict[str, Any])
async def get_single_news_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Fetch a single news article by ID."""
    stmt = select(NewsArticle).where(NewsArticle.id == article_id)
    res = await db.execute(stmt)
    article = res.scalar_one_or_none()

    if article:
        return {
            "id": str(article.id),
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "source_name": article.source_name,
            "source_url": article.source_url,
            "url": article.url,
            "published_at": article.published_at.isoformat(),
            "discovered_at": article.discovered_at.isoformat(),
            "company": article.company,
            "symbol": article.symbol,
            "exchange": article.exchange,
            "category": article.category,
            "content_hash": article.content_hash,
            "processing_status": article.processing_status,
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Article {article_id} not found",
    )
