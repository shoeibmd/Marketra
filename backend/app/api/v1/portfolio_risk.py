import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.domain import PortfolioRiskSnapshot, User
from app.services.analytics.portfolio_risk import PortfolioRiskService

router = APIRouter(prefix="/portfolio/risk", tags=["Portfolio Risk Analytics"])
logger = logging.getLogger("terminal.api.portfolio_risk")


class StressTestRequest(BaseModel):
    account_id: Optional[UUID] = None
    market_shock_pct: Optional[float] = Field(None, description="Global market shock percentage (e.g. -10.0)")
    sector_shocks: Optional[Dict[str, float]] = Field(None, description="Sector-specific shocks (e.g. {'IT': -10.0})")
    symbol_shocks: Optional[Dict[str, float]] = Field(None, description="Symbol-specific shocks (e.g. {'RELIANCE': -10.0})")
    scenario_name: str = Field("CUSTOM_SCENARIO", description="Name of hypothetical stress scenario")


@router.get("/summary", response_model=Dict[str, Any])
async def get_portfolio_risk_summary(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get comprehensive portfolio risk analytics summary."""
    service = PortfolioRiskService(db)
    var_es = await service.calculate_var_and_es(user_id=current_user.id, account_id=account_id)
    div = await service.calculate_diversification_metrics(user_id=current_user.id, account_id=account_id)
    contrib = await service.calculate_risk_contribution(user_id=current_user.id, account_id=account_id)
    return {
        "var_and_expected_shortfall": var_es,
        "diversification": div,
        "risk_contribution": contrib,
    }


@router.get("/var", response_model=Dict[str, Any])
async def get_portfolio_var(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    confidence_level: float = Query(0.95, description="Confidence level (0.90, 0.95, 0.99)"),
    lookback_days: int = Query(90, description="Lookback window in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get Value at Risk (Historical and Parametric)."""
    service = PortfolioRiskService(db)
    return await service.calculate_var_and_es(
        user_id=current_user.id,
        account_id=account_id,
        confidence_level=confidence_level,
        lookback_days=lookback_days,
    )


@router.get("/expected-shortfall", response_model=Dict[str, Any])
async def get_portfolio_expected_shortfall(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    confidence_level: float = Query(0.95, description="Confidence level (0.90, 0.95, 0.99)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get Expected Shortfall / Conditional VaR (CVaR)."""
    service = PortfolioRiskService(db)
    res = await service.calculate_var_and_es(
        user_id=current_user.id,
        account_id=account_id,
        confidence_level=confidence_level,
    )
    return {
        "data_quality_status": res.get("data_quality_status"),
        "confidence_level": confidence_level,
        "expected_shortfall": res.get("expected_shortfall"),
        "disclaimer": res.get("disclaimer"),
    }


@router.get("/correlation", response_model=Dict[str, Any])
async def get_portfolio_correlation(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    lookback_days: int = Query(30, description="Lookback period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get synchronized holding correlation matrix and highly correlated holding pairs."""
    service = PortfolioRiskService(db)
    return await service.calculate_correlation_matrix(
        user_id=current_user.id,
        account_id=account_id,
        lookback_days=lookback_days,
    )


@router.get("/diversification", response_model=Dict[str, Any])
async def get_portfolio_diversification(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get diversification score, HHI concentration, and top contributors."""
    service = PortfolioRiskService(db)
    return await service.calculate_diversification_metrics(
        user_id=current_user.id,
        account_id=account_id,
    )


@router.get("/contribution", response_model=Dict[str, Any])
async def get_portfolio_risk_contribution(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get marginal risk contribution by company and sector."""
    service = PortfolioRiskService(db)
    return await service.calculate_risk_contribution(
        user_id=current_user.id,
        account_id=account_id,
    )


@router.post("/stress-test", response_model=Dict[str, Any])
async def run_portfolio_stress_test(
    req: StressTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Run hypothetical stress test scenarios (market shocks, sector shocks, holding shocks)."""
    service = PortfolioRiskService(db)
    return await service.run_stress_test(
        user_id=current_user.id,
        account_id=req.account_id,
        market_shock_pct=req.market_shock_pct,
        sector_shocks=req.sector_shocks,
        symbol_shocks=req.symbol_shocks,
        scenario_name=req.scenario_name,
    )


@router.get("/history", response_model=Dict[str, Any])
async def get_portfolio_risk_history(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    limit: int = Query(30, description="Max snapshot history count"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get historical persisted risk analytics snapshots."""
    stmt = (
        select(PortfolioRiskSnapshot)
        .where(PortfolioRiskSnapshot.user_id == current_user.id)
        .order_by(PortfolioRiskSnapshot.timestamp.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    snaps = res.scalars().all()

    return {
        "snapshots": [
            {
                "id": str(s.id),
                "timestamp": s.timestamp.isoformat(),
                "portfolio_value": float(s.portfolio_value),
                "volatility_pct": float(s.volatility_pct) if s.volatility_pct else None,
                "var_95_pct": float(s.var_95_pct) if s.var_95_pct else None,
                "expected_shortfall_95_pct": float(s.expected_shortfall_95_pct) if s.expected_shortfall_95_pct else None,
                "drawdown_pct": float(s.drawdown_pct),
                "data_quality_status": s.data_quality_status,
                "diversification": s.diversification_metrics_json,
            }
            for s in snaps
        ]
    }
