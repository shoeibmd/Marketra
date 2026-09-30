from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import EventCompanyRelationship, FinancialEvent, Instrument, User
from app.schemas.ai import StructuredFinancialEvent
from app.services.ai.mock import MockAIProvider

router = APIRouter(prefix="/events", tags=["Financial Events"])
ai_provider = MockAIProvider()


def _format_event(event: FinancialEvent, company_roles: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "id": str(event.id),
        "news_id": str(event.news_id) if event.news_id else None,
        "cluster_id": event.cluster_id,
        "event_type": event.event_type,
        "event_title": event.event_title,
        "event_summary": event.event_summary,
        "event_date": event.event_date.isoformat(),
        "detected_at": event.detected_at.isoformat(),
        "primary_company_id": str(event.primary_company_id) if event.primary_company_id else None,
        "sector": event.sector or "General Equity",
        "importance": event.importance,
        "confidence": event.confidence,
        "source_name": event.source_name,
        "source_url": event.source_url,
        "verified_facts": event.verified_facts,
        "ai_analysis": event.ai_analysis_json,
        "potential_impact": event.potential_impact,
        "uncertainties": event.uncertainties,
        "company_roles": company_roles or [],
    }


@router.get("", response_model=dict[str, Any])
async def list_financial_events(
    event_type: str | None = Query(None, description="Filter by event type (e.g. ACQUISITION, RESULTS)"),
    importance: str | None = Query(None, description="Filter by importance (LOW, MEDIUM, HIGH, CRITICAL)"),
    sector: str | None = Query(None, description="Filter by sector"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 10: Paginated list of structured financial events."""
    offset = (page - 1) * page_size
    query = select(FinancialEvent)

    if event_type:
        query = query.where(FinancialEvent.event_type == event_type.upper().strip())
    if importance:
        query = query.where(FinancialEvent.importance == importance.upper().strip())
    if sector:
        query = query.where(FinancialEvent.sector.ilike(f"%{sector.strip()}%"))

    query = query.order_by(FinancialEvent.event_date.desc()).offset(offset).limit(page_size)
    res = await db.execute(query)
    events = res.scalars().all()

    items = []
    for ev in events:
        roles_stmt = (
            select(Instrument.symbol, Instrument.name, EventCompanyRelationship.role, EventCompanyRelationship.relationship_note)
            .join(EventCompanyRelationship)
            .where(EventCompanyRelationship.event_id == ev.id)
        )
        roles_res = await db.execute(roles_stmt)
        roles_list = [
            {"symbol": r[0], "company_name": r[1], "role": r[2], "note": r[3]} for r in roles_res.all()
        ]
        items.append(_format_event(ev, roles_list))

    return {
        "page": page,
        "page_size": page_size,
        "total_returned": len(items),
        "items": items,
    }


@router.get("/search", response_model=dict[str, Any])
async def search_financial_events(
    q: str | None = Query(None, description="Search query string"),
    symbol: str | None = Query(None, description="Filter by symbol"),
    sector: str | None = Query(None, description="Filter by sector"),
    event_type: str | None = Query(None, description="Filter by event type"),
    importance: str | None = Query(None, description="Filter by importance"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 10: Advanced multi-parameter financial event search with pagination."""
    offset = (page - 1) * page_size
    query = select(FinancialEvent)

    if symbol:
        sym_clean = symbol.upper().strip()
        subq = select(EventCompanyRelationship.event_id).join(Instrument).where(Instrument.symbol == sym_clean)
        query = query.where(FinancialEvent.id.in_(subq))

    if sector:
        query = query.where(FinancialEvent.sector.ilike(f"%{sector.strip()}%"))

    if event_type:
        query = query.where(FinancialEvent.event_type == event_type.upper().strip())

    if importance:
        query = query.where(FinancialEvent.importance == importance.upper().strip())

    if q:
        kw = f"%{q.strip()}%"
        query = query.where(or_(FinancialEvent.event_title.ilike(kw), FinancialEvent.event_summary.ilike(kw)))

    query = query.order_by(FinancialEvent.event_date.desc()).offset(offset).limit(page_size)
    res = await db.execute(query)
    events = res.scalars().all()

    items = [_format_event(ev) for ev in events]
    return {
        "page": page,
        "page_size": page_size,
        "total_returned": len(items),
        "items": items,
    }


@router.get("/company/{symbol}", response_model=dict[str, Any])
async def get_company_events(
    symbol: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 10: Fetch events associated with a company symbol."""
    sym_clean = symbol.upper().strip()
    offset = (page - 1) * page_size

    subq = select(EventCompanyRelationship.event_id).join(Instrument).where(Instrument.symbol == sym_clean)
    query = (
        select(FinancialEvent)
        .where(FinancialEvent.id.in_(subq))
        .order_by(FinancialEvent.event_date.desc())
        .offset(offset)
        .limit(page_size)
    )

    res = await db.execute(query)
    events = res.scalars().all()

    items = [_format_event(ev) for ev in events]
    return {
        "symbol": sym_clean,
        "page": page,
        "page_size": page_size,
        "total_returned": len(items),
        "items": items,
    }


@router.get("/company/{symbol}/timeline", response_model=dict[str, Any])
async def get_company_event_timeline(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 10: Historical company event timeline view."""
    sym_clean = symbol.upper().strip()

    subq = select(EventCompanyRelationship.event_id).join(Instrument).where(Instrument.symbol == sym_clean)
    query = (
        select(FinancialEvent)
        .where(FinancialEvent.id.in_(subq))
        .order_by(FinancialEvent.event_date.desc())
        .limit(20)
    )

    res = await db.execute(query)
    events = res.scalars().all()

    timeline_items = [
        {
            "id": str(ev.id),
            "date": ev.event_date.isoformat(),
            "event_type": ev.event_type,
            "title": ev.event_title,
            "importance": ev.importance,
            "summary": ev.event_summary,
        }
        for ev in events
    ]

    return {
        "symbol": sym_clean,
        "total_events": len(timeline_items),
        "timeline": timeline_items,
    }


@router.get("/company/{symbol}/relationships", response_model=dict[str, Any])
async def get_company_relationships(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 10: Fetch evidenced related companies and role interactions."""
    sym_clean = symbol.upper().strip()

    # Query events where company participates
    subq = select(EventCompanyRelationship.event_id).join(Instrument).where(Instrument.symbol == sym_clean)
    rel_stmt = (
        select(Instrument.symbol, Instrument.name, EventCompanyRelationship.role, EventCompanyRelationship.relationship_note)
        .join(EventCompanyRelationship)
        .where(EventCompanyRelationship.event_id.in_(subq), Instrument.symbol != sym_clean)
    )

    rel_res = await db.execute(rel_stmt)
    relationships = [
        {
            "symbol": r[0],
            "company_name": r[1],
            "role": r[2],
            "note": r[3] or f"Co-participant in event role {r[2]}",
        }
        for r in rel_res.all()
    ]

    return {
        "symbol": sym_clean,
        "related_companies": relationships,
    }


@router.get("/{event_id}", response_model=dict[str, Any])
async def get_single_event_details(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Phase 10: Fetch single financial event details with full role mappings."""
    stmt = select(FinancialEvent).where(FinancialEvent.id == event_id)
    res = await db.execute(stmt)
    ev = res.scalar_one_or_none()

    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} not found")

    roles_stmt = (
        select(Instrument.symbol, Instrument.name, EventCompanyRelationship.role, EventCompanyRelationship.relationship_note)
        .join(EventCompanyRelationship)
        .where(EventCompanyRelationship.event_id == ev.id)
    )
    roles_res = await db.execute(roles_stmt)
    roles_list = [
        {"symbol": r[0], "company_name": r[1], "role": r[2], "note": r[3]} for r in roles_res.all()
    ]

    return _format_event(ev, roles_list)
