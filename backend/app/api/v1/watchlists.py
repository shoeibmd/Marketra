import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import AlertPreference, Instrument, User, Watchlist, WatchlistCompany

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


class CreateWatchlistRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    is_default: bool = False


class AddCompanyRequest(BaseModel):
    symbol_or_isin: str = Field(..., min_length=1)


class UpdateAlertPreferenceRequest(BaseModel):
    minimum_importance: str = Field("HIGH", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    event_types: list[str] = Field(default_factory=list)
    filter_setting: str = "ALL_IMPORTANT_NEWS"


@router.get("", response_model=list[dict[str, Any]])
async def list_user_watchlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Get all watchlists belonging to the current user."""
    stmt = select(Watchlist).where(Watchlist.user_id == current_user.id).order_by(Watchlist.is_default.desc(), Watchlist.created_at.asc())
    res = await db.execute(stmt)
    watchlists = res.scalars().all()

    # If user has no watchlist, create default "My Watchlist"
    if not watchlists:
        default_wl = Watchlist(
            id=uuid.uuid4(),
            user_id=current_user.id,
            name="My Watchlist",
            description="Default personal watchlist",
            is_default=True,
        )
        db.add(default_wl)
        await db.commit()
        await db.refresh(default_wl)
        watchlists = [default_wl]

    result = []
    for wl in watchlists:
        comp_stmt = (
            select(Instrument.symbol, Instrument.name, Instrument.exchange_code, Instrument.sector)
            .join(WatchlistCompany)
            .where(WatchlistCompany.watchlist_id == wl.id)
        )
        comp_res = await db.execute(comp_stmt)
        companies = [
            {"symbol": r[0], "name": r[1], "exchange": r[2], "sector": r[3]} for r in comp_res.all()
        ]

        result.append(
            {
                "id": str(wl.id),
                "name": wl.name,
                "description": wl.description,
                "is_default": wl.is_default,
                "company_count": len(companies),
                "companies": companies,
                "created_at": wl.created_at.isoformat(),
            }
        )

    return result


@router.post("", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    req: CreateWatchlistRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new custom watchlist for current user."""
    wl = Watchlist(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=req.name,
        description=req.description,
        is_default=req.is_default,
    )
    db.add(wl)
    await db.commit()
    await db.refresh(wl)

    return {
        "id": str(wl.id),
        "name": wl.name,
        "description": wl.description,
        "is_default": wl.is_default,
        "created_at": wl.created_at.isoformat(),
    }


@router.get("/{watchlist_id}", response_model=dict[str, Any])
async def get_watchlist_detail(
    watchlist_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get watchlist by ID (enforces strict user ownership IDOR protection)."""
    try:
        wl_uuid = uuid.UUID(watchlist_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid watchlist ID format")

    stmt = select(Watchlist).where(Watchlist.id == wl_uuid)
    res = await db.execute(stmt)
    wl = res.scalar_one_or_none()

    if not wl or wl.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found or unauthorized")

    comp_stmt = (
        select(Instrument.id, Instrument.symbol, Instrument.name, Instrument.exchange_code, Instrument.sector)
        .join(WatchlistCompany)
        .where(WatchlistCompany.watchlist_id == wl.id)
    )
    comp_res = await db.execute(comp_stmt)
    companies = [
        {"id": str(r[0]), "symbol": r[1], "name": r[2], "exchange": r[3], "sector": r[4]} for r in comp_res.all()
    ]

    return {
        "id": str(wl.id),
        "name": wl.name,
        "description": wl.description,
        "is_default": wl.is_default,
        "companies": companies,
        "created_at": wl.created_at.isoformat(),
    }


@router.post("/{watchlist_id}/companies", response_model=dict[str, Any])
async def add_company_to_watchlist(
    watchlist_id: str,
    req: AddCompanyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Add company/instrument to watchlist by symbol or ISIN (prevents duplicate entries)."""
    try:
        wl_uuid = uuid.UUID(watchlist_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid watchlist ID format")

    stmt = select(Watchlist).where(Watchlist.id == wl_uuid)
    res = await db.execute(stmt)
    wl = res.scalar_one_or_none()

    if not wl or wl.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found or unauthorized")

    sym_clean = req.symbol_or_isin.upper().strip()
    inst_stmt = select(Instrument).where(
        or_(Instrument.symbol == sym_clean, Instrument.isin == sym_clean)
    )
    inst_res = await db.execute(inst_stmt)
    inst = inst_res.scalar_one_or_none()

    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instrument {sym_clean} not found")

    # Check for duplicate entry
    dup_stmt = select(WatchlistCompany).where(
        WatchlistCompany.watchlist_id == wl.id, WatchlistCompany.instrument_id == inst.id
    )
    dup_res = await db.execute(dup_stmt)
    if dup_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Company {inst.symbol} already in watchlist")

    wc = WatchlistCompany(
        id=uuid.uuid4(),
        watchlist_id=wl.id,
        instrument_id=inst.id,
    )
    db.add(wc)
    await db.commit()

    return {"status": "added", "symbol": inst.symbol, "name": inst.name}


@router.delete("/{watchlist_id}/companies/{symbol}", response_model=dict[str, Any])
async def remove_company_from_watchlist(
    watchlist_id: str,
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Remove company from watchlist."""
    try:
        wl_uuid = uuid.UUID(watchlist_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid watchlist ID format")

    stmt = select(Watchlist).where(Watchlist.id == wl_uuid)
    res = await db.execute(stmt)
    wl = res.scalar_one_or_none()

    if not wl or wl.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found or unauthorized")

    sym_clean = symbol.upper().strip()
    wc_stmt = (
        select(WatchlistCompany)
        .join(Instrument)
        .where(WatchlistCompany.watchlist_id == wl.id, Instrument.symbol == sym_clean)
    )
    wc_res = await db.execute(wc_stmt)
    wc = wc_res.scalar_one_or_none()

    if not wc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Symbol {sym_clean} not in watchlist")

    await db.delete(wc)
    await db.commit()

    return {"status": "removed", "symbol": sym_clean}


@router.get("/preferences/me", response_model=dict[str, Any])
async def get_user_alert_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get alert preferences for authenticated user."""
    stmt = select(AlertPreference).where(AlertPreference.user_id == current_user.id)
    res = await db.execute(stmt)
    pref = res.scalar_one_or_none()

    if not pref:
        pref = AlertPreference(
            id=uuid.uuid4(),
            user_id=current_user.id,
            minimum_importance="HIGH",
            event_types_json=[],
            filter_setting="ALL_IMPORTANT_NEWS",
        )
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    return {
        "minimum_importance": pref.minimum_importance,
        "event_types": pref.event_types_json,
        "filter_setting": pref.filter_setting,
    }


@router.put("/preferences/me", response_model=dict[str, Any])
async def update_user_alert_preferences(
    req: UpdateAlertPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update alert preferences for authenticated user."""
    stmt = select(AlertPreference).where(AlertPreference.user_id == current_user.id)
    res = await db.execute(stmt)
    pref = res.scalar_one_or_none()

    if not pref:
        pref = AlertPreference(
            id=uuid.uuid4(),
            user_id=current_user.id,
            minimum_importance=req.minimum_importance,
            event_types_json=req.event_types,
            filter_setting=req.filter_setting,
        )
        db.add(pref)
    else:
        pref.minimum_importance = req.minimum_importance
        pref.event_types_json = req.event_types
        pref.filter_setting = req.filter_setting
        db.add(pref)

    await db.commit()
    return {
        "status": "updated",
        "minimum_importance": req.minimum_importance,
        "filter_setting": req.filter_setting,
    }
