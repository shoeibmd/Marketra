import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.services.analytics.portfolio_analytics import PortfolioAnalyticsService

router = APIRouter(prefix="/portfolio-analytics", tags=["Portfolio Analytics"])
logger = logging.getLogger("terminal.api.portfolio_analytics")


@router.get("/summary", response_model=Dict[str, Any])
async def get_portfolio_analytics_summary(
    account_id: Optional[UUID] = Query(None, description="Specific paper trading account ID"),
    benchmark: str = Query("NIFTY50", description="Benchmark symbol (NIFTY50 / SENSEX)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get comprehensive portfolio risk and performance analytics for the authenticated user."""
    service = PortfolioAnalyticsService(db)
    analytics = await service.generate_portfolio_analytics(
        user_id=current_user.id,
        account_id=account_id,
        benchmark_symbol=benchmark,
    )
    return analytics


@router.get("/risk-ratios", response_model=Dict[str, Any])
async def get_portfolio_risk_ratios(
    account_id: Optional[UUID] = Query(None, description="Specific paper trading account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get standalone risk ratios (Sharpe, Sortino, Drawdown, Sector Concentration)."""
    service = PortfolioAnalyticsService(db)
    analytics = await service.generate_portfolio_analytics(
        user_id=current_user.id,
        account_id=account_id,
    )
    return {
        "account_id": analytics.get("account_id"),
        "data_status": analytics.get("data_status"),
        "risk_analytics": analytics.get("risk_analytics"),
        "disclaimer": analytics.get("disclaimer"),
    }
