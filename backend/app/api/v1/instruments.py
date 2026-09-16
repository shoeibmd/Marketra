from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_postgres_db
from app.schemas.market_data import NormalizedInstrument, NormalizedQuote
from app.services.providers.mock import MockProvider

router = APIRouter(prefix="/instruments", tags=["Instruments"])
mock_provider = MockProvider()


@router.get("/search", response_model=list[NormalizedInstrument])
async def search_instruments(
    q: str = Query(..., min_length=1, description="Search symbol or name"),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[NormalizedInstrument]:
    """Search instruments by symbol or name."""
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
