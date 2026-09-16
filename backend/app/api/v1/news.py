from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth.auth_service import get_current_user
from app.schemas.market_data import NormalizedNewsArticle
from app.services.providers.mock import MockProvider

router = APIRouter(prefix="/news", tags=["News"])
mock_provider = MockProvider()


@router.get("", response_model=list[NormalizedNewsArticle])
async def get_news_articles(
    symbol: str | None = Query(None, description="Filter news by instrument symbol"),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[NormalizedNewsArticle]:
    """Fetch news articles optionally filtered by instrument."""
    if symbol:
        inst = await mock_provider.get_instrument_by_symbol(symbol)
        if not inst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instrument {symbol} not found",
            )
        articles = await mock_provider.get_news(inst, limit=limit)
        return [NormalizedNewsArticle.model_validate(a) for a in articles]

    articles = await mock_provider.get_news(None, limit=limit)
    return [NormalizedNewsArticle.model_validate(a) for a in articles]


@router.get("/{article_id}", response_model=NormalizedNewsArticle)
async def get_single_news_article(
    article_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> NormalizedNewsArticle:
    """Fetch a single news article by ID."""
    all_articles = await mock_provider.get_news(None, limit=50)
    for article in all_articles:
        if str(article.id) == article_id:
            return NormalizedNewsArticle.model_validate(article)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Article {article_id} not found",
    )
