import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets import manager as ws_manager
from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import (
    BacktestJob,
    BacktestResult,
    Instrument,
    PaperOrder,
    PaperPosition,
    PaperTrade,
    User,
)
from app.services.paper.backtest_engine import BacktestEngine, StrategyRegistry
from app.services.paper.trading_engine import PaperTradingEngine

router = APIRouter(prefix="/paper", tags=["Paper Trading & Strategy Simulation"])


class CreateOrderRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    side: str = Field(..., pattern="^(BUY|SELL)$")
    quantity: float = Field(..., gt=0)
    order_type: str = Field("MARKET", pattern="^(MARKET|LIMIT)$")
    requested_price: float | None = Field(None, gt=0)


class RunBacktestRequest(BaseModel):
    strategy_name: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    initial_capital: float = Field(1000000.0, gt=0)
    parameters: dict[str, Any] = Field(default_factory=dict)


@router.get("/accounts/me", response_model=dict[str, Any])
async def get_my_paper_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get or initialize paper trading account for current user."""
    engine = PaperTradingEngine(db)
    account = await engine.get_or_create_account(current_user)

    # Fetch current quote prices for positions valuation
    prices: dict[uuid.UUID, Decimal] = {}
    pos_stmt = select(PaperPosition).where(PaperPosition.account_id == account.id, PaperPosition.quantity > Decimal("0"))
    pos_res = await db.execute(pos_stmt)
    positions = pos_res.scalars().all()

    for p in positions:
        inst_stmt = select(Instrument).where(Instrument.id == p.instrument_id)
        inst_res = await db.execute(inst_stmt)
        inst = inst_res.scalar_one_or_none()
        if inst:
            prices[inst.id] = p.average_entry_price

    summary = await engine.get_portfolio_summary(account, prices)
    return summary


@router.post("/accounts/me/orders", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def submit_paper_order(
    req: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Submit a simulated paper trading order with strict IDOR user authorization."""
    engine = PaperTradingEngine(db)
    account = await engine.get_or_create_account(current_user)

    sym_clean = req.symbol.upper().strip()
    inst_stmt = select(Instrument).where(Instrument.symbol == sym_clean)
    inst_res = await db.execute(inst_stmt)
    inst = inst_res.scalar_one_or_none()

    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instrument {sym_clean} not found")

    market_price = Decimal(str(req.requested_price)) if req.requested_price else Decimal("2450.00")

    try:
        order = await engine.place_order(
            account=account,
            instrument=inst,
            side=req.side,
            quantity=Decimal(str(req.quantity)),
            order_type=req.order_type,
            requested_price=Decimal(str(req.requested_price)) if req.requested_price else None,
            market_price=market_price,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # WebSocket Broadcast
    await ws_manager.broadcast(
        {
            "type": "paper_order_executed" if order.status == "EXECUTED" else "paper_order_rejected",
            "data": {
                "user_id": str(current_user.id),
                "order_id": str(order.id),
                "symbol": inst.symbol,
                "side": order.side,
                "status": order.status,
                "executed_price": float(order.executed_price) if order.executed_price else None,
                "rejection_reason": order.rejection_reason,
            },
        }
    )

    return {
        "id": str(order.id),
        "symbol": inst.symbol,
        "side": order.side,
        "order_type": order.order_type,
        "quantity": float(order.quantity),
        "executed_price": float(order.executed_price) if order.executed_price else None,
        "status": order.status,
        "rejection_reason": order.rejection_reason,
        "created_at": order.created_at.isoformat(),
    }


@router.get("/accounts/me/orders", response_model=list[dict[str, Any]])
async def list_my_paper_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all paper orders for current user."""
    engine = PaperTradingEngine(db)
    account = await engine.get_or_create_account(current_user)

    stmt = select(PaperOrder).where(PaperOrder.account_id == account.id).order_by(PaperOrder.created_at.desc())
    res = await db.execute(stmt)
    orders = res.scalars().all()

    result = []
    for o in orders:
        inst_stmt = select(Instrument).where(Instrument.id == o.instrument_id)
        inst_res = await db.execute(inst_stmt)
        inst = inst_res.scalar_one_or_none()
        result.append(
            {
                "id": str(o.id),
                "symbol": inst.symbol if inst else "UNKNOWN",
                "side": o.side,
                "order_type": o.order_type,
                "quantity": float(o.quantity),
                "requested_price": float(o.requested_price) if o.requested_price else None,
                "executed_price": float(o.executed_price) if o.executed_price else None,
                "status": o.status,
                "rejection_reason": o.rejection_reason,
                "created_at": o.created_at.isoformat(),
            }
        )
    return result


@router.get("/accounts/me/trades", response_model=list[dict[str, Any]])
async def list_my_paper_trades(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List execution trade ledger for current user."""
    engine = PaperTradingEngine(db)
    account = await engine.get_or_create_account(current_user)

    stmt = select(PaperTrade).where(PaperTrade.account_id == account.id).order_by(PaperTrade.executed_at.desc())
    res = await db.execute(stmt)
    trades = res.scalars().all()

    result = []
    for t in trades:
        inst_stmt = select(Instrument).where(Instrument.id == t.instrument_id)
        inst_res = await db.execute(inst_stmt)
        inst = inst_res.scalar_one_or_none()
        result.append(
            {
                "id": str(t.id),
                "order_id": str(t.order_id),
                "symbol": inst.symbol if inst else "UNKNOWN",
                "side": t.side,
                "quantity": float(t.quantity),
                "execution_price": float(t.execution_price),
                "fees": float(t.fees),
                "slippage": float(t.slippage),
                "realized_pnl": float(t.realized_pnl),
                "executed_at": t.executed_at.isoformat(),
            }
        )
    return result


@router.get("/strategies", response_model=list[dict[str, Any]])
async def list_trusted_strategies() -> list[dict[str, Any]]:
    """List server-side registered pre-built backtesting strategies."""
    return StrategyRegistry.get_supported_strategies()


@router.post("/backtests", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def run_strategy_backtest(
    req: RunBacktestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Execute deterministic strategy backtest with look-ahead bias protection."""
    # Check supported strategy
    supported = [s["name"] for s in StrategyRegistry.get_supported_strategies()]
    if req.strategy_name.upper() not in supported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported strategy '{req.strategy_name}'. Pre-built strategies available: {supported}",
        )

    job = BacktestJob(
        id=uuid.uuid4(),
        user_id=current_user.id,
        strategy_name=req.strategy_name.upper(),
        symbol=req.symbol.upper().strip(),
        initial_capital=Decimal(str(req.initial_capital)),
        parameters_json=req.parameters,
        status="RUNNING",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    engine = BacktestEngine(db)
    try:
        res = await engine.run_backtest(job)
    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "job_id": str(job.id),
        "strategy_name": job.strategy_name,
        "symbol": job.symbol,
        "status": job.status,
        "initial_capital": float(res.initial_capital),
        "final_equity": float(res.final_equity),
        "total_pnl": float(res.total_pnl),
        "total_return_pct": float(res.total_return_pct),
        "max_drawdown_pct": float(res.max_drawdown_pct),
        "trade_count": res.trade_count,
        "win_rate_pct": float(res.win_rate_pct),
        "equity_curve": res.equity_curve_json,
        "trades": res.trades_json,
        "disclaimer": "HISTORICAL SIMULATION RESULTS ONLY — NO REAL BROKER OR LIVE ORDERS",
    }


@router.get("/backtests/{job_id}", response_model=dict[str, Any])
async def get_backtest_result(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get backtest results (strict user IDOR protection)."""
    try:
        j_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid job ID format")

    stmt = select(BacktestJob).where(BacktestJob.id == j_uuid)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()

    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backtest job not found or unauthorized")

    result_stmt = select(BacktestResult).where(BacktestResult.job_id == job.id)
    result_res = await db.execute(result_stmt)
    result = result_res.scalar_one_or_none()

    if not result:
        return {"job_id": str(job.id), "status": job.status, "error_message": job.error_message}

    return {
        "job_id": str(job.id),
        "strategy_name": job.strategy_name,
        "symbol": job.symbol,
        "status": job.status,
        "initial_capital": float(result.initial_capital),
        "final_equity": float(result.final_equity),
        "total_pnl": float(result.total_pnl),
        "total_return_pct": float(result.total_return_pct),
        "max_drawdown_pct": float(result.max_drawdown_pct),
        "trade_count": result.trade_count,
        "win_rate_pct": float(result.win_rate_pct),
        "equity_curve": result.equity_curve_json,
        "trades": result.trades_json,
    }
