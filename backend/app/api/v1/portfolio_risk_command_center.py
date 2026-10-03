import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.services.analytics.portfolio_risk_command_center import PortfolioRiskCommandCenterService

router = APIRouter(prefix="/portfolio/risk-command-center", tags=["Portfolio Risk Command Center"])
logger = logging.getLogger("terminal.api.portfolio_risk_command_center")


@router.get("", response_model=Dict[str, Any])
async def get_portfolio_risk_command_center(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get consolidated Portfolio Risk Command Center analytics."""
    svc = PortfolioRiskCommandCenterService(db)
    return await svc.get_command_center_data(user_id=current_user.id, account_id=account_id)


@router.get("/history", response_model=Dict[str, Any])
async def get_portfolio_risk_command_center_history(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get historical risk trends for the Command Center."""
    svc = PortfolioRiskCommandCenterService(db)
    data = await svc.get_command_center_data(user_id=current_user.id, account_id=account_id)
    return {
        "timestamp": data.get("timestamp"),
        "risk_trends": data.get("risk_trends", []),
        "data_quality": data.get("data_quality_center"),
    }


@router.get("/export", response_model=Dict[str, Any])
async def export_portfolio_risk_command_center_report(
    account_id: Optional[UUID] = Query(None, description="Paper trading account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Export structured Markdown & JSON Portfolio Risk Report."""
    svc = PortfolioRiskCommandCenterService(db)
    return await svc.generate_exportable_risk_report(user_id=current_user.id, account_id=account_id)
