import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import BrokerOrderMapping, Instrument, User
from app.services.trading.order_service import OrderService

router = APIRouter(prefix="/trading", tags=["Unified Trading & Order Management"])


class CreateTradingOrderRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    side: str = Field(..., pattern="^(BUY|SELL)$")
    quantity: float = Field(..., gt=0)
    execution_mode: str = Field("PAPER", pattern="^(PAPER|LIVE)$")
    order_type: str = Field("MARKET", pattern="^(MARKET|LIMIT)$")
    requested_price: float | None = Field(None, gt=0)
    client_order_id: str | None = None


@router.post("/orders", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def submit_trading_order(
    req: CreateTradingOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Submit a trading order through RiskEngine and execution adapter (strict IDOR user authorization)."""
    sym_clean = req.symbol.upper().strip()
    inst_stmt = select(Instrument).where(Instrument.symbol == sym_clean)
    inst_res = await db.execute(inst_stmt)
    inst = inst_res.scalar_one_or_none()

    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instrument {sym_clean} not found")

    service = OrderService(db)
    mapping = await service.submit_order(
        user=current_user,
        instrument=inst,
        side=req.side,
        quantity=Decimal(str(req.quantity)),
        execution_mode=req.execution_mode,
        order_type=req.order_type,
        requested_price=Decimal(str(req.requested_price)) if req.requested_price else None,
        client_order_id=req.client_order_id,
    )

    return {
        "client_order_id": mapping.client_order_id,
        "broker_order_id": mapping.broker_order_id,
        "execution_mode": mapping.execution_mode,
        "symbol": inst.symbol,
        "side": mapping.side,
        "quantity": float(mapping.quantity),
        "status": mapping.status,
        "rejection_reason": mapping.rejection_reason,
        "created_at": mapping.created_at.isoformat(),
    }


@router.get("/orders", response_model=list[dict[str, Any]])
async def list_trading_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List current user's trading orders across PAPER and LIVE modes."""
    stmt = (
        select(BrokerOrderMapping, Instrument.symbol)
        .join(Instrument, Instrument.id == BrokerOrderMapping.instrument_id)
        .where(BrokerOrderMapping.user_id == current_user.id)
        .order_by(BrokerOrderMapping.created_at.desc())
    )
    res = await db.execute(stmt)
    rows = res.all()

    return [
        {
            "client_order_id": m.client_order_id,
            "broker_order_id": m.broker_order_id,
            "execution_mode": m.execution_mode,
            "symbol": sym,
            "side": m.side,
            "quantity": float(m.quantity),
            "status": m.status,
            "rejection_reason": m.rejection_reason,
            "created_at": m.created_at.isoformat(),
        }
        for m, sym in rows
    ]


@router.get("/orders/{client_order_id}", response_model=dict[str, Any])
async def get_trading_order_detail(
    client_order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get single trading order detail by client_order_id (enforces strict user IDOR protection)."""
    stmt = (
        select(BrokerOrderMapping, Instrument.symbol)
        .join(Instrument, Instrument.id == BrokerOrderMapping.instrument_id)
        .where(
            BrokerOrderMapping.client_order_id == client_order_id,
            BrokerOrderMapping.user_id == current_user.id,
        )
    )
    res = await db.execute(stmt)
    row = res.one_or_none()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or unauthorized")

    m, sym = row
    return {
        "client_order_id": m.client_order_id,
        "broker_order_id": m.broker_order_id,
        "execution_mode": m.execution_mode,
        "symbol": sym,
        "side": m.side,
        "quantity": float(m.quantity),
        "status": m.status,
        "rejection_reason": m.rejection_reason,
        "created_at": m.created_at.isoformat(),
    }
