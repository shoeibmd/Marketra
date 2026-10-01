from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import RiskDecision, User
from app.services.risk.risk_engine import RiskEngine

router = APIRouter(prefix="/risk", tags=["Pre-Trade Risk Engine"])


@router.get("/status", response_model=dict[str, Any])
async def get_risk_engine_status(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get server-side safety gate controls and live trading flags."""
    engine = RiskEngine(db)
    return {
        "live_trading_enabled": engine.live_trading_enabled,
        "trading_kill_switch": engine.trading_kill_switch,
        "risk_engine_enabled": engine.risk_engine_enabled,
        "broker_configured": engine.broker_configured,
        "disclaimer": "Production safety defaults: LIVE_TRADING_ENABLED=false, TRADING_KILL_SWITCH=true",
    }


@router.get("/limits", response_model=dict[str, Any])
async def get_user_risk_limits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get user's pre-trade risk thresholds."""
    engine = RiskEngine(db)
    limits = await engine.get_or_create_user_risk_limits(current_user)

    return {
        "user_id": str(current_user.id),
        "max_order_quantity": float(limits.max_order_quantity),
        "max_order_value": float(limits.max_order_value),
        "max_portfolio_exposure_pct": float(limits.max_portfolio_exposure_pct),
        "daily_loss_limit": float(limits.daily_loss_limit),
        "max_open_orders": limits.max_open_orders,
    }


@router.get("/decisions", response_model=list[dict[str, Any]])
async def list_user_risk_decisions(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List recent risk evaluation decisions for current user."""
    stmt = (
        select(RiskDecision)
        .where(RiskDecision.user_id == current_user.id)
        .order_by(RiskDecision.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    decisions = res.scalars().all()

    return [
        {
            "id": str(d.id),
            "client_order_id": d.client_order_id,
            "rule_name": d.rule_name,
            "input_value": d.input_value,
            "threshold_value": d.threshold_value,
            "decision": d.decision,
            "reason": d.reason,
            "created_at": d.created_at.isoformat(),
        }
        for d in decisions
    ]
