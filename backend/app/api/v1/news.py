from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import ArticleInstrument, Instrument, NewsArticle, User
from app.services.ai.mock import MockAIProvider
from app.services.news.rss import RSSNewsProvider

router = APIRouter(prefix="/news", tags=["News"])
rss_provider = RSSNewsProvider()
ai_provider = MockAIProvider()


def _format_article(article: NewsArticle, matching_symbols: list[str] | None = None) -> dict[str, Any]:
    analysis = article.ai_analysis_json
    if not analysis and article.ai_status == "completed":
        analysis = {
            "what_happened": article.title,
            "primary_company_affected": article.company or article.symbol or "Listed Entity",
            "related_companies": [],
            "event_category": article.category,
            "importance_reason": "Automated market disclosure analysis.",
            "source_facts": [f"Source: {article.source_name}", f"Headline: {article.title}"],
            "potential_impact": article.ai_impact or "NEUTRAL",
            "importance_level": article.ai_importance or "MEDIUM",
            "ai_confidence": 0.90,
            "user_monitoring_checklist": ["Monitor upcoming NSE/BSE filings."],
            "related_sector": "Equity Market",
            "related_announcements": [],
            "uncertainties_or_gaps": ["NOT AVAILABLE FROM SOURCE: Specific financial guidance was omitted."],
            "model_used": "mock-financial-rag-v1",
        }

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
        "associated_symbols": matching_symbols or ([article.symbol] if article.symbol else []),
        "ai_status": article.ai_status or "pending",
        "ai_importance": article.ai_importance,
        "ai_impact": article.ai_impact,
        "ai_analysis": analysis,
    }


@router.get("", response_model=list[dict[str, Any]])
async def get_news_articles(
    symbol: str | None = Query(None, description="Filter news by instrument symbol"),
    category: str | None = Query(None, description="Filter news by category"),
    exchange: str | None = Query(None, description="Filter news by exchange (NSE, BSE)"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Legacy Endpoint: Fetch live Indian market news articles with AI analysis."""
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
        return [_format_article(a) for a in articles]

    # Provider sample fallback
    live_items = await rss_provider.fetch_news()
    filtered = live_items
    if symbol:
        filtered = [i for i in filtered if i.symbol == symbol.upper().strip()]
    if category:
        filtered = [i for i in filtered if i.category == category.lower().strip()]
    if exchange:
        filtered = [i for i in filtered if i.exchange == exchange.upper().strip()]

    result: list[dict[str, Any]] = []
    for i in filtered[:limit]:
        analysis = await ai_provider.generate_news_analysis(i.title, i.summary, i.company, i.symbol, i.source_name)
        result.append(
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
                "associated_symbols": [i.symbol] if i.symbol else [],
                "ai_status": "completed",
                "ai_importance": analysis.importance_level,
                "ai_impact": analysis.potential_impact,
                "ai_analysis": analysis.model_dump(),
            }
        )
    return result


@router.get("/live", response_model=dict[str, Any])
async def get_live_news_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category: str | None = Query(None),
    exchange: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 3: Paginated Live Stream News Feed with AI Intelligence."""
    offset = (page - 1) * page_size
    query = select(NewsArticle)

    if category:
        query = query.where(NewsArticle.category == category.lower().strip())
    if exchange:
        query = query.where(NewsArticle.exchange == exchange.upper().strip())

    query = query.order_by(NewsArticle.published_at.desc()).offset(offset).limit(page_size)
    res = await db.execute(query)
    articles = res.scalars().all()

    items = [_format_article(a) for a in articles]
    return {
        "page": page,
        "page_size": page_size,
        "total_returned": len(items),
        "items": items,
    }


@router.get("/search", response_model=dict[str, Any])
async def search_news(
    q: str | None = Query(None, description="Keyword search query"),
    company: str | None = Query(None, description="Company name query"),
    symbol: str | None = Query(None, description="Instrument symbol query"),
    sector: str | None = Query(None, description="Industry sector filter"),
    category: str | None = Query(None, description="News category filter"),
    date_from: datetime | None = Query(None, description="Filter articles published after date"),
    date_to: datetime | None = Query(None, description="Filter articles published before date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 3: Full-featured Server-Side News Search with Structured AI Intelligence."""
    offset = (page - 1) * page_size
    query = select(NewsArticle)

    if symbol:
        sym_clean = symbol.upper().strip()
        subq = select(ArticleInstrument.article_id).join(Instrument).where(Instrument.symbol == sym_clean)
        query = query.where(or_(NewsArticle.symbol == sym_clean, NewsArticle.id.in_(subq)))

    if sector:
        sec_clean = sector.lower().strip()
        subq_sec = select(ArticleInstrument.article_id).where(ArticleInstrument.sector.ilike(f"%{sec_clean}%"))
        query = query.where(NewsArticle.id.in_(subq_sec))

    if company:
        comp_clean = f"%{company.strip()}%"
        query = query.where(NewsArticle.company.ilike(comp_clean))

    if q:
        kw = f"%{q.strip()}%"
        query = query.where(or_(NewsArticle.title.ilike(kw), NewsArticle.summary.ilike(kw)))

    if category:
        query = query.where(NewsArticle.category == category.lower().strip())

    if date_from:
        query = query.where(NewsArticle.published_at >= date_from)

    if date_to:
        query = query.where(NewsArticle.published_at <= date_to)

    query = query.order_by(NewsArticle.published_at.desc()).offset(offset).limit(page_size)
    res = await db.execute(query)
    articles = res.scalars().all()

    items = [_format_article(a) for a in articles]
    return {
        "page": page,
        "page_size": page_size,
        "total_returned": len(items),
        "items": items,
    }


@router.get("/company/{symbol}", response_model=dict[str, Any])
async def get_company_news(
    symbol: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 3: Fetch company news mapped via primary or junction associations with AI Analysis."""
    sym_clean = symbol.upper().strip()
    offset = (page - 1) * page_size

    subq = select(ArticleInstrument.article_id).join(Instrument).where(Instrument.symbol == sym_clean)
    query = (
        select(NewsArticle)
        .where(or_(NewsArticle.symbol == sym_clean, NewsArticle.id.in_(subq)))
        .order_by(NewsArticle.published_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    res = await db.execute(query)
    articles = res.scalars().all()

    items = [_format_article(a) for a in articles]
    return {
        "symbol": sym_clean,
        "page": page,
        "page_size": page_size,
        "total_returned": len(items),
        "items": items,
    }


@router.get("/{article_id}", response_model=dict[str, Any])
async def get_single_news_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Fetch a single news article by ID with AI analysis."""
    stmt = select(NewsArticle).where(NewsArticle.id == article_id)
    res = await db.execute(stmt)
    article = res.scalar_one_or_none()

    if article:
        junc_stmt = (
            select(Instrument.symbol)
            .join(ArticleInstrument)
            .where(ArticleInstrument.article_id == article.id)
        )
        junc_res = await db.execute(junc_stmt)
        associated_syms = list(junc_res.scalars().all())

        return _format_article(article, matching_symbols=associated_syms)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Article {article_id} not found",
    )
