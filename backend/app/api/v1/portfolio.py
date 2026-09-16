import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth.auth_service import get_current_user
from app.schemas.portfolio import (
    PortfolioSummaryResponse,
    TransactionCreateRequest,
    TransactionResponse,
)
from app.services.providers.mock import MockProvider

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])
mock_provider = MockProvider()

_MOCK_TRANSACTIONS: list[dict[str, Any]] = [
    {
        "id": str(uuid.uuid4()),
        "symbol": "AAPL",
        "transaction_type": "BUY",
        "quantity": 10.0,
        "price": 170.0,
        "total_value": 1700.0,
        "timestamp": datetime.now(UTC).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "symbol": "BTC-USD",
        "transaction_type": "BUY",
        "quantity": 0.5,
        "price": 60000.0,
        "total_value": 30000.0,
        "timestamp": datetime.now(UTC).isoformat(),
    },
]


@router.get("", response_model=dict[str, Any])
async def get_user_portfolio(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Fetch user portfolio with current positions and live valuations."""
    positions = []
    for tx in _MOCK_TRANSACTIONS:
        inst = await mock_provider.get_instrument_by_symbol(tx["symbol"])
        if inst:
            quote = await mock_provider.get_realtime_quote(inst)
            qty = float(tx["quantity"])
            cost_px = float(tx["price"])
            mkt_val = qty * quote.last_price
            cost_basis = qty * cost_px
            pnl = mkt_val - cost_basis

            positions.append(
                {
                    "symbol": inst.symbol,
                    "name": inst.name,
                    "quantity": qty,
                    "average_buy_price": cost_px,
                    "current_price": quote.last_price,
                    "market_value": round(mkt_val, 2),
                    "unrealized_pnl": round(pnl, 2),
                    "unrealized_pnl_percent": round((pnl / cost_basis) * 100, 2),
                }
            )

    return {
        "portfolio_name": "Main Growth Portfolio",
        "currency": "USD",
        "cash_balance": 25000.0,
        "positions": positions,
    }


@router.post("/transactions", response_model=TransactionResponse)
async def create_portfolio_transaction(
    tx_req: TransactionCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> TransactionResponse:
    """Record a buy/sell transaction."""
    inst = await mock_provider.get_instrument_by_symbol(tx_req.symbol)
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {tx_req.symbol} not found",
        )

    tot_val = tx_req.quantity * tx_req.price
    tx_id = str(uuid.uuid4())
    now_str = datetime.now(UTC).isoformat()

    record = {
        "id": tx_id,
        "symbol": inst.symbol,
        "transaction_type": tx_req.transaction_type,
        "quantity": tx_req.quantity,
        "price": tx_req.price,
        "total_value": round(tot_val, 2),
        "timestamp": now_str,
    }
    _MOCK_TRANSACTIONS.append(record)
    return TransactionResponse(
        id=tx_id,
        symbol=inst.symbol,
        transaction_type=tx_req.transaction_type,
        quantity=tx_req.quantity,
        price=tx_req.price,
        total_value=round(tot_val, 2),
        timestamp=now_str,
    )


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_portfolio_transactions(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[TransactionResponse]:
    """Fetch transaction history."""
    return [
        TransactionResponse(
            id=str(tx["id"]),
            symbol=str(tx["symbol"]),
            transaction_type=str(tx["transaction_type"]),
            quantity=float(tx["quantity"]),
            price=float(tx["price"]),
            total_value=float(tx["total_value"]),
            timestamp=str(tx["timestamp"]),
        )
        for tx in _MOCK_TRANSACTIONS
    ]


@router.get("/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PortfolioSummaryResponse:
    """Fetch aggregated portfolio P&L and asset metrics."""
    tot_val = 0.0
    tot_cost = 0.0

    for tx in _MOCK_TRANSACTIONS:
        inst = await mock_provider.get_instrument_by_symbol(tx["symbol"])
        if inst:
            q = await mock_provider.get_realtime_quote(inst)
            qty = float(tx["quantity"])
            px = float(tx["price"])
            tot_val += qty * q.last_price
            tot_cost += qty * px

    pnl = tot_val - tot_cost
    pnl_pct = (pnl / tot_cost * 100) if tot_cost > 0 else 0.0

    return PortfolioSummaryResponse(
        portfolio_name="Main Growth Portfolio",
        currency="USD",
        cash_balance=25000.0,
        total_market_value=round(tot_val, 2),
        total_pnl=round(pnl, 2),
        total_pnl_percent=round(pnl_pct, 2),
        positions_count=len(_MOCK_TRANSACTIONS),
    )
