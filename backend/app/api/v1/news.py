from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import ArticleInstrument, Instrument, NewsArticle, User
from app.services.ai.mock import MockAIProvider
from app.services.providers.mock import MockProvider
from app.services.news.rss import RSSNewsProvider

router = APIRouter(prefix="/news", tags=["News"])
rss_provider = RSSNewsProvider()
ai_provider = MockAIProvider()
mock_market_provider = MockProvider()

CATEGORY_MAPPINGS = {
    "results": ["corporate_earnings", "results", "earnings"],
    "corporate": ["corporate_actions", "corporate_earnings", "corporate", "business_update"],
    "acquisition": ["acquisition", "merger", "business_update"],
    "investment": ["investment", "expansion", "business_update"],
    "dividend": ["corporate_actions", "dividend"],
    "regulatory": ["regulation", "regulator", "monetary_policy", "central_bank"],
    "market": ["general", "market_index", "macro"],
}


async def _get_market_context_for_symbol(symbol: str) -> dict[str, Any] | None:
    """Helper to fetch live quote & sector market context for a symbol."""
    if not symbol:
        return None

    inst = await mock_market_provider.get_instrument_by_symbol(symbol)
    if not inst:
        return None

    q = await mock_market_provider.get_realtime_quote(inst)
    fund = await mock_market_provider.get_fundamentals(inst)

    prev_close = round(q.last_price * 0.992, 2)
    pct_change = round(((q.last_price - prev_close) / prev_close) * 100, 2)

    return {
        "symbol": inst.symbol,
        "company_name": inst.name,
        "currency": inst.currency,
        "current_price": q.last_price,
        "previous_close": prev_close,
        "change_percent": pct_change,
        "volume": q.last_size * 1250,
        "sector": inst.sector or "General Equity",
        "market_relevance_note": (
            "Price movement occurred around the same period. "
            "Possible market relevance; does not imply direct causation."
        ),
        "high_52_week": fund.high_52_week if fund else None,
        "low_52_week": fund.low_52_week if fund else None,
    }


async def _format_article(
    article: NewsArticle,
    matching_symbols: list[str] | None = None,
) -> dict[str, Any]:
    analysis = article.ai_analysis_json
    primary_sym = article.symbol or (matching_symbols[0] if matching_symbols else None)
    market_context = await _get_market_context_for_symbol(primary_sym) if primary_sym else None

    # Fetch market context for related companies
    related_syms = matching_symbols or ([article.symbol] if article.symbol else [])
    related_contexts = []
    for sym in related_syms:
        if sym != primary_sym:
            ctx = await _get_market_context_for_symbol(sym)
            if ctx:
                related_contexts.append(ctx)

    if not analysis and article.ai_status == "completed":
        analysis = {
            "what_happened": article.title,
            "primary_company_affected": article.company or article.symbol or "Listed Entity",
            "related_companies": related_syms,
            "event_category": article.category,
            "importance_reason": "Automated market disclosure analysis.",
            "source_facts": [f"Source: {article.source_name}", f"Headline: {article.title}"],
            "potential_impact": article.ai_impact or "NEUTRAL",
            "importance_level": article.ai_importance or "MEDIUM",
            "ai_confidence": 0.90,
            "user_monitoring_checklist": ["Monitor upcoming NSE/BSE filings."],
            "related_sector": market_context["sector"] if market_context else "Equity Market",
            "related_announcements": [f"Previous disclosures for {article.company or article.symbol or 'Entity'}"],
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
        "associated_symbols": related_syms,
        "ai_status": article.ai_status or "pending",
        "ai_importance": article.ai_importance or "MEDIUM",
        "ai_impact": article.ai_impact or "NEUTRAL",
        "ai_analysis": analysis,
        "market_context": market_context,
        "related_market_contexts": related_contexts,
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
    """Legacy Endpoint: Fetch live Indian market news articles with AI & Market Context."""
    query = select(NewsArticle)

    if symbol:
        query = query.where(NewsArticle.symbol == symbol.upper().strip())
    if category:
        cat_key = category.lower().strip()
        cat_targets = CATEGORY_MAPPINGS.get(cat_key, [cat_key])
        query = query.where(NewsArticle.category.in_(cat_targets))
    if exchange:
        query = query.where(NewsArticle.exchange == exchange.upper().strip())

    query = query.order_by(NewsArticle.published_at.desc()).limit(limit)
    res = await db.execute(query)
    articles = res.scalars().all()

    if articles:
        return [await _format_article(a) for a in articles]

    # Provider sample fallback
    live_items = await rss_provider.fetch_news()
    filtered = live_items
    if symbol:
        filtered = [i for i in filtered if i.symbol == symbol.upper().strip()]
    if category:
        cat_key = category.lower().strip()
        cat_targets = CATEGORY_MAPPINGS.get(cat_key, [cat_key])
        filtered = [i for i in filtered if i.category in cat_targets]
    if exchange:
        filtered = [i for i in filtered if i.exchange == exchange.upper().strip()]

    result: list[dict[str, Any]] = []
    for i in filtered[:limit]:
        analysis = await ai_provider.generate_news_analysis(i.title, i.summary, i.company, i.symbol, i.source_name)
        m_ctx = await _get_market_context_for_symbol(i.symbol) if i.symbol else None
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
                "market_context": m_ctx,
                "related_market_contexts": [],
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
    """Phase 6: Paginated Live Stream News Feed with AI & Market Correlation."""
    offset = (page - 1) * page_size
    query = select(NewsArticle)

    if category:
        cat_key = category.lower().strip()
        cat_targets = CATEGORY_MAPPINGS.get(cat_key, [cat_key])
        query = query.where(NewsArticle.category.in_(cat_targets))

    if exchange:
        query = query.where(NewsArticle.exchange == exchange.upper().strip())

    query = query.order_by(NewsArticle.published_at.desc()).offset(offset).limit(page_size)
    res = await db.execute(query)
    articles = res.scalars().all()

    items = [await _format_article(a) for a in articles]
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
    """Phase 6: News Search with Correlated Market Context."""
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
        cat_key = category.lower().strip()
        cat_targets = CATEGORY_MAPPINGS.get(cat_key, [cat_key])
        query = query.where(NewsArticle.category.in_(cat_targets))

    if date_from:
        query = query.where(NewsArticle.published_at >= date_from)

    if date_to:
        query = query.where(NewsArticle.published_at <= date_to)

    query = query.order_by(NewsArticle.published_at.desc()).offset(offset).limit(page_size)
    res = await db.execute(query)
    articles = res.scalars().all()

    items = [await _format_article(a) for a in articles]
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
    """Phase 6: Fetch company news mapped with Market Context."""
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

    items = [await _format_article(a) for a in articles]
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
    """Fetch a single news article by ID with Market Context."""
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

        return await _format_article(article, matching_symbols=associated_syms)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Article {article_id} not found",
    )
