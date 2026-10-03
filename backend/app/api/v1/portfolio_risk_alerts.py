import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.domain import PortfolioRiskAlert, PortfolioRiskAlertPreference, User
from app.services.analytics.portfolio_risk_monitoring import PortfolioRiskMonitoringService

router = APIRouter(prefix="/portfolio/risk/alerts", tags=["Portfolio Risk Alerts"])
logger = logging.getLogger("terminal.api.portfolio_risk_alerts")


class UpdatePreferenceRequest(BaseModel):
    drawdown_threshold_pct: Optional[float] = Field(None, ge=0.1, le=100.0)
    daily_loss_threshold_pct: Optional[float] = Field(None, ge=0.1, le=100.0)
    daily_loss_threshold_amount: Optional[float] = Field(None, ge=1.0)
    var_threshold_pct: Optional[float] = Field(None, ge=0.1, le=100.0)
    expected_shortfall_threshold_pct: Optional[float] = Field(None, ge=0.1, le=100.0)
    company_concentration_threshold_pct: Optional[float] = Field(None, ge=1.0, le=100.0)
    sector_concentration_threshold_pct: Optional[float] = Field(None, ge=1.0, le=100.0)
    correlation_threshold: Optional[float] = Field(None, ge=0.1, le=1.0)
    volatility_threshold_pct: Optional[float] = Field(None, ge=0.1, le=100.0)
    cooldown_minutes: Optional[int] = Field(None, ge=1, le=1440)
    enabled_alerts_json: Optional[List[str]] = None


@router.get("", response_model=List[Dict[str, Any]])
async def get_risk_alerts(
    status_filter: Optional[str] = Query(None, description="TRIGGERED, RECOVERED"),
    severity: Optional[str] = Query(None, description="INFO, WARNING, CRITICAL"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get user risk alerts filtered by status and severity."""
    stmt = select(PortfolioRiskAlert).where(PortfolioRiskAlert.user_id == current_user.id)
    if status_filter:
        stmt = stmt.where(PortfolioRiskAlert.status == status_filter.upper())
    if severity:
        stmt = stmt.where(PortfolioRiskAlert.severity == severity.upper())

    stmt = stmt.order_by(PortfolioRiskAlert.triggered_at.desc()).limit(limit)
    res = await db.execute(stmt)
    alerts = res.scalars().all()

    return [
        {
            "id": str(a.id),
            "alert_type": a.alert_type,
            "severity": a.severity,
            "metric_name": a.metric_name,
            "current_value": float(a.current_value),
            "threshold_value": float(a.threshold_value),
            "unit": a.unit,
            "status": a.status,
            "data_quality_status": a.data_quality_status,
            "affected_symbols": a.affected_symbols_json,
            "affected_sectors": a.affected_sectors_json,
            "explanation": a.explanation,
            "triggered_at": a.triggered_at.isoformat(),
            "recovered_at": a.recovered_at.isoformat() if a.recovered_at else None,
            "is_read": a.is_read,
        }
        for a in alerts
    ]


@router.get("/active", response_model=List[Dict[str, Any]])
async def get_active_risk_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get active TRIGGERED risk alerts."""
    return await get_risk_alerts(status_filter="TRIGGERED", limit=50, db=db, current_user=current_user)


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_risk_alerts_history(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get historical risk alerts log."""
    return await get_risk_alerts(limit=limit, db=db, current_user=current_user)


@router.get("/preferences", response_model=Dict[str, Any])
async def get_risk_alert_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get user risk alert preferences."""
    svc = PortfolioRiskMonitoringService(db)
    pref = await svc.get_or_create_alert_preference(current_user.id)
    return {
        "drawdown_threshold_pct": float(pref.drawdown_threshold_pct),
        "daily_loss_threshold_pct": float(pref.daily_loss_threshold_pct),
        "daily_loss_threshold_amount": float(pref.daily_loss_threshold_amount),
        "var_threshold_pct": float(pref.var_threshold_pct),
        "expected_shortfall_threshold_pct": float(pref.expected_shortfall_threshold_pct),
        "company_concentration_threshold_pct": float(pref.company_concentration_threshold_pct),
        "sector_concentration_threshold_pct": float(pref.sector_concentration_threshold_pct),
        "correlation_threshold": float(pref.correlation_threshold),
        "volatility_threshold_pct": float(pref.volatility_threshold_pct),
        "cooldown_minutes": pref.cooldown_minutes,
        "enabled_alerts": pref.enabled_alerts_json,
    }


@router.put("/preferences", response_model=Dict[str, Any])
async def update_risk_alert_preferences(
    req: UpdatePreferenceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update user risk alert preferences."""
    svc = PortfolioRiskMonitoringService(db)
    pref = await svc.get_or_create_alert_preference(current_user.id)

    if req.drawdown_threshold_pct is not None:
        pref.drawdown_threshold_pct = Decimal(str(req.drawdown_threshold_pct))
    if req.daily_loss_threshold_pct is not None:
        pref.daily_loss_threshold_pct = Decimal(str(req.daily_loss_threshold_pct))
    if req.daily_loss_threshold_amount is not None:
        pref.daily_loss_threshold_amount = Decimal(str(req.daily_loss_threshold_amount))
    if req.var_threshold_pct is not None:
        pref.var_threshold_pct = Decimal(str(req.var_threshold_pct))
    if req.expected_shortfall_threshold_pct is not None:
        pref.expected_shortfall_threshold_pct = Decimal(str(req.expected_shortfall_threshold_pct))
    if req.company_concentration_threshold_pct is not None:
        pref.company_concentration_threshold_pct = Decimal(str(req.company_concentration_threshold_pct))
    if req.sector_concentration_threshold_pct is not None:
        pref.sector_concentration_threshold_pct = Decimal(str(req.sector_concentration_threshold_pct))
    if req.correlation_threshold is not None:
        pref.correlation_threshold = Decimal(str(req.correlation_threshold))
    if req.volatility_threshold_pct is not None:
        pref.volatility_threshold_pct = Decimal(str(req.volatility_threshold_pct))
    if req.cooldown_minutes is not None:
        pref.cooldown_minutes = req.cooldown_minutes
    if req.enabled_alerts_json is not None:
        pref.enabled_alerts_json = req.enabled_alerts_json

    await db.commit()
    return await get_risk_alert_preferences(db=db, current_user=current_user)


@router.post("/preferences/reset", response_model=Dict[str, Any])
async def reset_risk_alert_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Reset user risk alert preferences to system defaults."""
    stmt = select(PortfolioRiskAlertPreference).where(PortfolioRiskAlertPreference.user_id == current_user.id)
    res = await db.execute(stmt)
    pref = res.scalar_one_or_none()
    if pref:
        await db.delete(pref)
        await db.commit()

    return await get_risk_alert_preferences(db=db, current_user=current_user)


@router.post("/{alert_id}/read", response_model=Dict[str, Any])
async def mark_risk_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Mark a risk alert as read."""
    stmt = select(PortfolioRiskAlert).where(
        PortfolioRiskAlert.id == alert_id,
        PortfolioRiskAlert.user_id == current_user.id,
    )
    res = await db.execute(stmt)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk alert not found.")

    alert.is_read = True
    await db.commit()
    return {"status": "success", "alert_id": str(alert_id), "is_read": True}


@router.post("/test", response_model=Dict[str, Any])
async def trigger_risk_monitoring_evaluation(
    account_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Trigger portfolio risk evaluation cycle on demand."""
    svc = PortfolioRiskMonitoringService(db)
    triggered = await svc.evaluate_user_portfolio_risk(user_id=current_user.id, account_id=account_id)
    return {
        "status": "completed",
        "evaluated_user_id": str(current_user.id),
        "triggered_alerts_count": len(triggered),
        "triggered_alerts": [
            {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "severity": a.severity,
                "current_value": float(a.current_value),
                "threshold_value": float(a.threshold_value),
            }
            for a in triggered
        ],
    }
