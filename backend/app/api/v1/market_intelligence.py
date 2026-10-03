import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.analytics.market_intelligence_service import MarketIntelligenceService

router = APIRouter(prefix="/market-intelligence", tags=["Market Intelligence"])
logger = logging.getLogger("terminal.api.market_intelligence")


@router.get("/overview", response_model=Dict[str, Any])
async def get_market_intelligence_overview(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get market-wide overview indices and breadth analytics."""
    svc = MarketIntelligenceService(db)
    return await svc.get_market_overview_and_breadth()


@router.get("/breadth", response_model=Dict[str, Any])
async def get_market_breadth(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get standalone market breadth metrics."""
    svc = MarketIntelligenceService(db)
    res = await svc.get_market_overview_and_breadth()
    return {
        "timestamp": res.get("timestamp"),
        "market_breadth": res.get("market_breadth"),
        "data_quality_status": res.get("data_quality_status"),
        "disclaimer": res.get("disclaimer"),
    }


@router.get("/sectors", response_model=Dict[str, Any])
async def get_sector_intelligence(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get sector returns, volatility, and sector correlation matrix."""
    svc = MarketIntelligenceService(db)
    return await svc.get_sector_intelligence()


@router.get("/regime", response_model=Dict[str, Any])
async def get_market_regime(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get descriptive historical market regime classification."""
    svc = MarketIntelligenceService(db)
    return await svc.get_market_regime()


@router.get("/anomalies", response_model=List[Dict[str, Any]])
async def detect_market_anomalies(
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Detect statistically unusual market price/volume anomalies."""
    svc = MarketIntelligenceService(db)
    recs = await svc.detect_market_anomalies()
    return [
        {
            "id": str(r.id),
            "anomaly_type": r.anomaly_type,
            "symbol": r.symbol,
            "sector": r.sector,
            "observed_value": float(r.observed_value),
            "baseline_value": float(r.baseline_value),
            "deviation_pct": float(r.deviation_pct),
            "description": r.description,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in recs
    ]
