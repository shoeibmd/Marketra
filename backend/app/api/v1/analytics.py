import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import EventCompanyRelationship, EventMarketObservation, FinancialEvent, Instrument
from app.services.analytics.event_market_analytics import EventMarketAnalyticsService

router = APIRouter(tags=["Historical Market Analytics"])


@router.get("/events/{event_id}/market-context", response_model=dict[str, Any])
async def get_event_market_context(
    event_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get factual historical market context & window observations around a financial event."""
    try:
        e_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event ID format")

    event_stmt = select(FinancialEvent).where(FinancialEvent.id == e_uuid)
    event_res = await db.execute(event_stmt)
    event = event_res.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial event not found")

    # Check existing observation
    obs_stmt = select(EventMarketObservation).where(EventMarketObservation.event_id == event.id)
    obs_res = await db.execute(obs_stmt)
    obs = obs_res.scalar_one_or_none()

    if not obs:
        # Calculate on the fly if instrument available
        if event.primary_company_id:
            inst_stmt = select(Instrument).where(Instrument.id == event.primary_company_id)
            inst_res = await db.execute(inst_stmt)
            inst = inst_res.scalar_one_or_none()
            if inst:
                service = EventMarketAnalyticsService(db)
                obs = await service.calculate_event_observation(event, inst)

    return {
        "event_id": str(event.id),
        "event_title": event.event_title,
        "event_type": event.event_type,
        "event_date": event.event_date.isoformat(),
        "importance": event.importance,
        "market_context": {
            "session_classification": obs.session_classification if obs else "UNCLASSIFIED",
            "baseline_timestamp": obs.baseline_timestamp.isoformat() if obs and obs.baseline_timestamp else None,
            "baseline_price": obs.baseline_price if obs else None,
            "return_1d_pct": obs.return_1d_pct if obs else None,
            "return_3d_pct": obs.return_3d_pct if obs else None,
            "return_5d_pct": obs.return_5d_pct if obs else None,
            "return_10d_pct": obs.return_10d_pct if obs else None,
            "return_20d_pct": obs.return_20d_pct if obs else None,
            "volume_before": obs.volume_before if obs else None,
            "volume_after": obs.volume_after if obs else None,
            "volume_change_pct": obs.volume_change_pct if obs else None,
            "data_status": obs.data_status if obs else "INSUFFICIENT",
            "disclaimer": "Historical observations reflect past price measurements and do not prove event causation or predict future movements.",
        },
    }


@router.get("/company/{symbol}/event-analytics", response_model=dict[str, Any])
async def get_company_event_analytics(
    symbol: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get company-specific historical event analytics and return observations."""
    sym_clean = symbol.upper().strip()
    inst_stmt = select(Instrument).where(Instrument.symbol == sym_clean)
    inst_res = await db.execute(inst_stmt)
    inst = inst_res.scalar_one_or_none()

    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instrument {sym_clean} not found")

    rel_stmt = (
        select(FinancialEvent, EventCompanyRelationship.role)
        .join(EventCompanyRelationship, EventCompanyRelationship.event_id == FinancialEvent.id)
        .where(EventCompanyRelationship.instrument_id == inst.id)
        .order_by(FinancialEvent.event_date.desc())
    )
    rel_res = await db.execute(rel_stmt)
    events_with_roles = rel_res.all()

    service = EventMarketAnalyticsService(db)
    observations: list[EventMarketObservation] = []

    for event, _ in events_with_roles:
        obs = await service.calculate_event_observation(event, inst)
        observations.append(obs)

    stats_1d = EventMarketAnalyticsService.compute_aggregate_statistics(observations, "1d")
    stats_5d = EventMarketAnalyticsService.compute_aggregate_statistics(observations, "5d")

    return {
        "symbol": inst.symbol,
        "company_name": inst.name,
        "total_events": len(events_with_roles),
        "aggregate_statistics_1d": stats_1d,
        "aggregate_statistics_5d": stats_5d,
        "observations": [
            {
                "event_id": str(obs.event_id),
                "event_date": obs.event_timestamp.isoformat(),
                "session": obs.session_classification,
                "baseline_price": obs.baseline_price,
                "return_1d_pct": obs.return_1d_pct,
                "return_5d_pct": obs.return_5d_pct,
                "data_status": obs.data_status,
            }
            for obs in observations[:20]
        ],
        "disclaimer": "Factual historical analysis only. Not an investment recommendation.",
    }


@router.get("/analytics/event-types", response_model=dict[str, Any])
async def get_event_type_analytics(
    event_type: str = Query("ACQUISITION"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get aggregate historical statistics for a specific financial event type across all companies."""
    ev_type_clean = event_type.upper().strip()
    events_stmt = select(FinancialEvent).where(FinancialEvent.event_type == ev_type_clean)
    events_res = await db.execute(events_stmt)
    events = events_res.scalars().all()

    service = EventMarketAnalyticsService(db)
    observations: list[EventMarketObservation] = []

    for event in events:
        if event.primary_company_id:
            inst_stmt = select(Instrument).where(Instrument.id == event.primary_company_id)
            inst_res = await db.execute(inst_stmt)
            inst = inst_res.scalar_one_or_none()
            if inst:
                obs = await service.calculate_event_observation(event, inst)
                observations.append(obs)

    stats_1d = EventMarketAnalyticsService.compute_aggregate_statistics(observations, "1d")
    stats_5d = EventMarketAnalyticsService.compute_aggregate_statistics(observations, "5d")

    return {
        "event_type": ev_type_clean,
        "total_historical_events": len(events),
        "aggregate_statistics_1d": stats_1d,
        "aggregate_statistics_5d": stats_5d,
        "disclaimer": "Aggregate historical return observations are non-causal statistical summaries.",
    }


@router.get("/analytics/compare", response_model=dict[str, Any])
async def compare_company_event_analytics(
    symbol1: str = Query(...),
    symbol2: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Side-by-side factual comparison of historical event observations between two companies."""
    s1_clean = symbol1.upper().strip()
    s2_clean = symbol2.upper().strip()

    c1_data = await get_company_event_analytics(s1_clean, db)
    c2_data = await get_company_event_analytics(s2_clean, db)

    return {
        "comparison": [
            {
                "symbol": c1_data["symbol"],
                "company_name": c1_data["company_name"],
                "total_events": c1_data["total_events"],
                "aggregate_statistics_1d": c1_data["aggregate_statistics_1d"],
                "aggregate_statistics_5d": c1_data["aggregate_statistics_5d"],
            },
            {
                "symbol": c2_data["symbol"],
                "company_name": c2_data["company_name"],
                "total_events": c2_data["total_events"],
                "aggregate_statistics_1d": c2_data["aggregate_statistics_1d"],
                "aggregate_statistics_5d": c2_data["aggregate_statistics_5d"],
            },
        ],
        "disclaimer": "Factual comparison of historical observations. Does not imply target prices or performance forecasts.",
    }
