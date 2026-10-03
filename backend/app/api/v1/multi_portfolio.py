import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.services.analytics.multi_portfolio_service import MultiPortfolioService

router = APIRouter(prefix="/portfolios", tags=["Multi-Portfolio Intelligence"])
logger = logging.getLogger("terminal.api.multi_portfolio")


class CreatePortfolioRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    initial_cash: float = Field(1000000.0, ge=1000.0)
    portfolio_type: str = Field("PAPER", description="MANUAL, PAPER, BROKER, STRATEGY, CUSTOM")


@router.get("", response_model=List[Dict[str, Any]])
async def list_user_portfolios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """List all portfolios owned by the authenticated user."""
    svc = MultiPortfolioService(db)
    accounts = await svc.list_user_portfolios(current_user.id)
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "portfolio_type": a.portfolio_type,
            "initial_cash": float(a.initial_cash),
            "available_cash": float(a.available_cash),
            "created_at": a.created_at.isoformat(),
        }
        for a in accounts
    ]


@router.post("", response_model=Dict[str, Any])
async def create_user_portfolio(
    req: CreatePortfolioRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create a new portfolio account."""
    svc = MultiPortfolioService(db)
    acct = await svc.create_portfolio_account(
        user_id=current_user.id,
        name=req.name,
        initial_cash=Decimal(str(req.initial_cash)),
        portfolio_type=req.portfolio_type,
    )
    return {
        "id": str(acct.id),
        "name": acct.name,
        "portfolio_type": acct.portfolio_type,
        "initial_cash": float(acct.initial_cash),
        "available_cash": float(acct.available_cash),
        "created_at": acct.created_at.isoformat(),
    }


@router.get("/compare", response_model=List[Dict[str, Any]])
async def compare_user_portfolios(
    account_ids: Optional[List[UUID]] = Query(None, description="List of portfolio account IDs to compare"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Side-by-side factual comparison of user-owned portfolios."""
    svc = MultiPortfolioService(db)
    return await svc.compare_portfolios(user_id=current_user.id, account_ids=account_ids)


@router.get("/consolidated", response_model=Dict[str, Any])
async def get_consolidated_multi_portfolio(
    account_ids: Optional[List[UUID]] = Query(None, description="List of portfolio account IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get aggregated multi-portfolio summary across user accounts."""
    svc = MultiPortfolioService(db)
    return await svc.get_consolidated_portfolio(user_id=current_user.id, account_ids=account_ids)


@router.get("/consolidated/exposure", response_model=List[Dict[str, Any]])
async def get_duplicate_exposures(
    account_ids: Optional[List[UUID]] = Query(None, description="List of portfolio account IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Detect companies and sectors held across multiple user portfolios."""
    svc = MultiPortfolioService(db)
    return await svc.detect_duplicate_exposures(user_id=current_user.id, account_ids=account_ids)


@router.get("/consolidated/attribution", response_model=Dict[str, Any])
async def get_multi_portfolio_attribution(
    account_ids: Optional[List[UUID]] = Query(None, description="List of portfolio account IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get performance P&L attribution across accounts."""
    svc = MultiPortfolioService(db)
    return await svc.get_portfolio_attribution(user_id=current_user.id, account_ids=account_ids)
