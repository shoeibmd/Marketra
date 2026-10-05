from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_postgres_db
from app.schemas.market_data import NormalizedInstrument, NormalizedQuote
from app.services.providers.mock import MockProvider

router = APIRouter(prefix="/instruments", tags=["Instruments"])
mock_provider = MockProvider()


from sqlalchemy import or_, select
from app.models.domain import Instrument

@router.get("/search", response_model=list[NormalizedInstrument])
async def search_instruments(
    q: str = Query(..., min_length=1, description="Search symbol or name"),
    db: AsyncSession = Depends(get_postgres_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[NormalizedInstrument]:
    """Search instruments by symbol or name in PostgreSQL database, with fallback to MockProvider."""
    term = f"%{q.strip().upper()}%"
    stmt = (
        select(Instrument)
        .where(
            Instrument.is_active == True,  # noqa: E712
            or_(
                Instrument.symbol.ilike(term),
                Instrument.name.ilike(term),
            ),
        )
        .limit(20)
    )
    db_res = await db.execute(stmt)
    db_instruments = db_res.scalars().all()

    if db_instruments:
        results = []
        for inst in db_instruments:
            results.append(
                NormalizedInstrument(
                    id=inst.id,
                    symbol=inst.symbol,
                    exchange_code=inst.exchange_code,
                    name=inst.name,
                    isin=inst.isin,
                    currency=inst.currency,
                    instrument_type=inst.instrument_type,
                    provider_symbol=f"NSE:{inst.symbol}",
                )
            )
        return results

    # Fallback to provider search if DB has not been seeded yet or for dynamic queries
    res = await mock_provider.search_instruments(q)
    return [NormalizedInstrument.model_validate(item) for item in res]


@router.get("/{instrument_id_or_symbol}", response_model=NormalizedInstrument)
async def get_instrument_details(
    instrument_id_or_symbol: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> NormalizedInstrument:
    """Get details for a single instrument by UUID or symbol."""
    inst = await mock_provider.get_instrument_by_symbol(instrument_id_or_symbol)
    if inst:
        return NormalizedInstrument.model_validate(inst)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Instrument {instrument_id_or_symbol} not found",
    )


@router.get("/{instrument_id_or_symbol}/quote", response_model=NormalizedQuote)
async def get_instrument_quote(
    instrument_id_or_symbol: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> NormalizedQuote:
    """Get latest realtime quote for an instrument."""
    inst = await mock_provider.get_instrument_by_symbol(instrument_id_or_symbol)
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {instrument_id_or_symbol} not found",
        )
    quote = await mock_provider.get_realtime_quote(inst)
    return NormalizedQuote.model_validate(quote)
