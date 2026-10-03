import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.domain import PortfolioBriefing, PortfolioBriefingPreference, PortfolioChangeEvent, User
from app.services.analytics.portfolio_briefing_service import PortfolioBriefingService
from app.services.analytics.portfolio_change_detection import PortfolioChangeDetectionService

router = APIRouter(prefix="/portfolio/briefings", tags=["Portfolio Briefings"])
logger = logging.getLogger("terminal.api.portfolio_briefings")


class GenerateBriefingRequest(BaseModel):
    account_id: Optional[UUID] = None
    briefing_type: str = Field("DAILY", description="DAILY, PRE_MARKET, INTRADAY, WEEKLY")


class UpdateBriefingPreferenceRequest(BaseModel):
    daily_briefing_enabled: Optional[bool] = None
    weekly_briefing_enabled: Optional[bool] = None
    pre_market_briefing_enabled: Optional[bool] = None
    intraday_briefing_enabled: Optional[bool] = None
    preferred_delivery_time: Optional[str] = None
    minimum_significance: Optional[str] = None
    sections_config_json: Optional[Dict[str, Any]] = None


@router.get("", response_model=List[Dict[str, Any]])
async def get_portfolio_briefings(
    briefing_type: Optional[str] = Query(None, description="DAILY, PRE_MARKET, INTRADAY, WEEKLY"),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Fetch user portfolio briefings list."""
    stmt = select(PortfolioBriefing).where(PortfolioBriefing.user_id == current_user.id)
    if briefing_type:
        stmt = stmt.where(PortfolioBriefing.briefing_type == briefing_type.upper())

    stmt = stmt.order_by(PortfolioBriefing.generated_at.desc()).limit(limit)
    res = await db.execute(stmt)
    briefings = res.scalars().all()

    return [
        {
            "id": str(b.id),
            "briefing_type": b.briefing_type,
            "status": b.status,
            "significance": b.significance,
            "summary_title": b.summary_title,
            "data_quality_status": b.data_quality_status,
            "generated_at": b.generated_at.isoformat(),
            "period_start": b.period_start.isoformat(),
            "period_end": b.period_end.isoformat(),
            "is_read": b.is_read,
        }
        for b in briefings
    ]


@router.get("/changes", response_model=List[Dict[str, Any]])
async def get_portfolio_change_events(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Fetch real-time detected portfolio change events timeline."""
    stmt = (
        select(PortfolioChangeEvent)
        .where(PortfolioChangeEvent.user_id == current_user.id)
        .order_by(PortfolioChangeEvent.detected_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    changes = res.scalars().all()

    return [
        {
            "id": str(c.id),
            "change_type": c.change_type,
            "significance": c.significance,
            "previous_value": float(c.previous_value) if c.previous_value is not None else None,
            "current_value": float(c.current_value) if c.current_value is not None else None,
            "absolute_change": float(c.absolute_change) if c.absolute_change is not None else None,
            "percentage_change": float(c.percentage_change) if c.percentage_change is not None else None,
            "affected_symbols": c.affected_symbols_json,
            "description": c.description,
            "detected_at": c.detected_at.isoformat(),
        }
        for c in changes
    ]


@router.get("/preferences", response_model=Dict[str, Any])
async def get_briefing_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Fetch user briefing preferences."""
    svc = PortfolioBriefingService(db)
    pref = await svc.get_or_create_briefing_preference(current_user.id)
    return {
        "daily_briefing_enabled": pref.daily_briefing_enabled,
        "weekly_briefing_enabled": pref.weekly_briefing_enabled,
        "pre_market_briefing_enabled": pref.pre_market_briefing_enabled,
        "intraday_briefing_enabled": pref.intraday_briefing_enabled,
        "preferred_delivery_time": pref.preferred_delivery_time,
        "minimum_significance": pref.minimum_significance,
        "sections_config": pref.sections_config_json,
    }


@router.put("/preferences", response_model=Dict[str, Any])
async def update_briefing_preferences(
    req: UpdateBriefingPreferenceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update user briefing preferences."""
    svc = PortfolioBriefingService(db)
    pref = await svc.get_or_create_briefing_preference(current_user.id)

    if req.daily_briefing_enabled is not None:
        pref.daily_briefing_enabled = req.daily_briefing_enabled
    if req.weekly_briefing_enabled is not None:
        pref.weekly_briefing_enabled = req.weekly_briefing_enabled
    if req.pre_market_briefing_enabled is not None:
        pref.pre_market_briefing_enabled = req.pre_market_briefing_enabled
    if req.intraday_briefing_enabled is not None:
        pref.intraday_briefing_enabled = req.intraday_briefing_enabled
    if req.preferred_delivery_time is not None:
        pref.preferred_delivery_time = req.preferred_delivery_time
    if req.minimum_significance is not None:
        pref.minimum_significance = req.minimum_significance
    if req.sections_config_json is not None:
        pref.sections_config_json = req.sections_config_json

    await db.commit()
    return await get_briefing_preferences(db=db, current_user=current_user)


@router.get("/{briefing_id}", response_model=Dict[str, Any])
async def get_briefing_detail(
    briefing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Fetch detailed briefing payload."""
    stmt = select(PortfolioBriefing).where(
        PortfolioBriefing.id == briefing_id,
        PortfolioBriefing.user_id == current_user.id,
    )
    res = await db.execute(stmt)
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing not found.")

    return {
        "id": str(b.id),
        "briefing_type": b.briefing_type,
        "status": b.status,
        "significance": b.significance,
        "summary_title": b.summary_title,
        "content": b.content_json,
        "sources": b.sources_json,
        "data_quality_status": b.data_quality_status,
        "generated_at": b.generated_at.isoformat(),
        "period_start": b.period_start.isoformat(),
        "period_end": b.period_end.isoformat(),
        "is_read": b.is_read,
    }


@router.post("/generate", response_model=Dict[str, Any])
async def generate_briefing_on_demand(
    req: GenerateBriefingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Generate portfolio briefing on demand."""
    svc = PortfolioBriefingService(db)
    briefing = await svc.generate_briefing(
        user_id=current_user.id,
        briefing_type=req.briefing_type,
        account_id=req.account_id,
    )
    return {
        "status": "completed",
        "briefing_id": str(briefing.id),
        "summary_title": briefing.summary_title,
        "generated_at": briefing.generated_at.isoformat(),
    }


@router.post("/{briefing_id}/read", response_model=Dict[str, Any])
async def mark_briefing_read(
    briefing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Mark briefing as read."""
    stmt = select(PortfolioBriefing).where(
        PortfolioBriefing.id == briefing_id,
        PortfolioBriefing.user_id == current_user.id,
    )
    res = await db.execute(stmt)
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing not found.")

    b.is_read = True
    await db.commit()
    return {"status": "success", "briefing_id": str(briefing_id), "is_read": True}
