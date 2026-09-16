from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth.auth_service import get_current_user
from app.schemas.market_data import NormalizedOHLCV
from app.services.providers.mock import MockProvider

router = APIRouter(prefix="/market", tags=["Market Data"])
mock_provider = MockProvider()


@router.get("/ohlcv/{symbol}", response_model=list[NormalizedOHLCV])
async def get_historical_ohlcv(
    symbol: str,
    interval: str = Query("1d", pattern="^(1m|5m|1h|1d)$"),
    days_back: int = Query(30, ge=1, le=730),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[NormalizedOHLCV]:
    """Fetch historical OHLCV chart candles for an instrument."""
    inst = await mock_provider.get_instrument_by_symbol(symbol)
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {symbol} not found",
        )

    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(days=days_back)
    res = await mock_provider.get_historical_ohlcv(inst, interval=interval, start_time=start_time, end_time=end_time)
    return [NormalizedOHLCV.model_validate(c) for c in res]


@router.get("/overview")
async def get_market_overview(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Fetch high-level market overview summary (indices, top gainers, losers)."""
    indices = ["SPY", "AAPL", "MSFT", "GOOGL", "BTC-USD"]
    quotes: list[dict[str, Any]] = []

    for sym in indices:
        inst = await mock_provider.get_instrument_by_symbol(sym)
        if inst:
            q = await mock_provider.get_realtime_quote(inst)
            quotes.append(
                {
                    "symbol": inst.symbol,
                    "name": inst.name,
                    "last_price": q.last_price,
                    "change_percent": 0.85 if "BTC" in sym else 0.35,
                }
            )

    return {
        "status": "active",
        "market_status": "OPEN",
        "indices": quotes,
        "gainers": quotes[:2],
        "losers": quotes[2:],
    }


@router.get("/watchlist")
async def get_default_watchlist(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Fetch user watchlist with live quotes."""
    symbols = ["AAPL", "MSFT", "TSLA", "BTC-USD", "ETH-USD"]
    watchlist: list[dict[str, Any]] = []

    for sym in symbols:
        inst = await mock_provider.get_instrument_by_symbol(sym)
        if inst:
            q = await mock_provider.get_realtime_quote(inst)
            watchlist.append(
                {
                    "symbol": inst.symbol,
                    "name": inst.name,
                    "currency": inst.currency,
                    "quote": q.model_dump(),
                }
            )

    return watchlist
