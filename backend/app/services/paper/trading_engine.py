import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    Instrument,
    PaperOrder,
    PaperPortfolioSnapshot,
    PaperPosition,
    PaperTrade,
    PaperTradingAccount,
    User,
)

logger = logging.getLogger("terminal.paper_engine")


class PaperTradingEngine:
    """Simulated paper trading execution engine using exact Decimal precision."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_account(
        self,
        user: User,
        account_name: str = "Primary Paper Account",
        initial_cash: Decimal = Decimal("1000000.00"),
    ) -> PaperTradingAccount:
        """Get or create user's primary paper trading account."""
        stmt = select(PaperTradingAccount).where(PaperTradingAccount.user_id == user.id)
        res = await self.db.execute(stmt)
        acc = res.scalar_one_or_none()

        if not acc:
            acc = PaperTradingAccount(
                id=uuid.uuid4(),
                user_id=user.id,
                name=account_name,
                initial_cash=initial_cash,
                available_cash=initial_cash,
            )
            self.db.add(acc)
            await self.db.commit()
            await self.db.refresh(acc)

        return acc

    async def place_order(
        self,
        account: PaperTradingAccount,
        instrument: Instrument,
        side: str,
        quantity: Decimal,
        order_type: str = "MARKET",
        requested_price: Decimal | None = None,
        market_price: Decimal | None = None,
        slippage_pct: Decimal = Decimal("0.0005"),  # 0.05% default
        fee_amount: Decimal = Decimal("20.00"),       # ₹20 fixed simulated fee
    ) -> PaperOrder:
        """Validate, record, and simulate execution of a paper trading order."""
        side_clean = side.upper().strip()
        type_clean = order_type.upper().strip()

        if quantity <= Decimal("0"):
            raise ValueError("INVALID_QUANTITY: Quantity must be positive")

        exec_price = market_price if market_price else requested_price
        if not exec_price or exec_price <= Decimal("0"):
            raise ValueError("MARKET_DATA_UNAVAILABLE: Valid market price is required for paper execution")

        # Apply slippage
        if side_clean == "BUY":
            effective_exec_price = exec_price * (Decimal("1") + slippage_pct)
        else:
            effective_exec_price = exec_price * (Decimal("1") - slippage_pct)

        effective_exec_price = round(effective_exec_price, 4)
        total_cost = (quantity * effective_exec_price) + fee_amount

        # Validate BUY cash
        if side_clean == "BUY":
            if account.available_cash < total_cost:
                order = PaperOrder(
                    id=uuid.uuid4(),
                    account_id=account.id,
                    instrument_id=instrument.id,
                    side=side_clean,
                    order_type=type_clean,
                    quantity=quantity,
                    requested_price=requested_price,
                    status="REJECTED",
                    rejection_reason=f"INSUFFICIENT_CASH: Needed ₹{total_cost}, available ₹{account.available_cash}",
                )
                self.db.add(order)
                await self.db.commit()
                return order

        # Validate SELL holdings
        pos = await self._get_position(account.id, instrument.id)
        if side_clean == "SELL":
            curr_qty = pos.quantity if pos else Decimal("0")
            if curr_qty < quantity:
                order = PaperOrder(
                    id=uuid.uuid4(),
                    account_id=account.id,
                    instrument_id=instrument.id,
                    side=side_clean,
                    order_type=type_clean,
                    quantity=quantity,
                    requested_price=requested_price,
                    status="REJECTED",
                    rejection_reason=f"INSUFFICIENT_POSITION: Holding {curr_qty}, requested sell {quantity}",
                )
                self.db.add(order)
                await self.db.commit()
                return order

        # Execute Order
        order = PaperOrder(
            id=uuid.uuid4(),
            account_id=account.id,
            instrument_id=instrument.id,
            side=side_clean,
            order_type=type_clean,
            quantity=quantity,
            requested_price=requested_price,
            executed_price=effective_exec_price,
            status="EXECUTED",
        )
        self.db.add(order)

        # Update Position & Realized P&L
        realized_pnl = Decimal("0.00")
        if not pos:
            pos = PaperPosition(
                id=uuid.uuid4(),
                account_id=account.id,
                instrument_id=instrument.id,
                quantity=Decimal("0"),
                average_entry_price=Decimal("0"),
                realized_pnl=Decimal("0.00"),
            )
            self.db.add(pos)

        if side_clean == "BUY":
            new_qty = pos.quantity + quantity
            if new_qty > Decimal("0"):
                new_avg = ((pos.quantity * pos.average_entry_price) + (quantity * effective_exec_price)) / new_qty
                pos.average_entry_price = round(new_avg, 4)
            pos.quantity = new_qty
            account.available_cash -= total_cost
        elif side_clean == "SELL":
            realized_pnl = round(((effective_exec_price - pos.average_entry_price) * quantity) - fee_amount, 2)
            pos.quantity -= quantity
            pos.realized_pnl += realized_pnl
            account.available_cash += round((quantity * effective_exec_price) - fee_amount, 2)

        # Create Paper Trade Execution Record
        trade = PaperTrade(
            id=uuid.uuid4(),
            account_id=account.id,
            order_id=order.id,
            instrument_id=instrument.id,
            side=side_clean,
            quantity=quantity,
            execution_price=effective_exec_price,
            fees=fee_amount,
            slippage=round(abs(effective_exec_price - exec_price), 4),
            realized_pnl=realized_pnl,
        )
        self.db.add(trade)

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def _get_position(self, account_id: uuid.UUID, instrument_id: uuid.UUID) -> PaperPosition | None:
        stmt = select(PaperPosition).where(
            PaperPosition.account_id == account_id,
            PaperPosition.instrument_id == instrument_id,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_portfolio_summary(
        self,
        account: PaperTradingAccount,
        current_prices: dict[uuid.UUID, Decimal],
    ) -> dict[str, Any]:
        """Calculate complete portfolio equity, realized P&L, unrealized P&L, and return %."""
        stmt = select(PaperPosition).where(PaperPosition.account_id == account.id, PaperPosition.quantity > Decimal("0"))
        res = await self.db.execute(stmt)
        positions = res.scalars().all()

        positions_val = Decimal("0.00")
        unrealized_pnl = Decimal("0.00")
        realized_pnl = Decimal("0.00")

        pos_list = []
        for p in positions:
            ltp = current_prices.get(p.instrument_id, p.average_entry_price)
            mkt_val = round(p.quantity * ltp, 2)
            unreal_pnl = round((ltp - p.average_entry_price) * p.quantity, 2)

            positions_val += mkt_val
            unrealized_pnl += unreal_pnl
            realized_pnl += p.realized_pnl

            pos_list.append(
                {
                    "instrument_id": str(p.instrument_id),
                    "quantity": float(p.quantity),
                    "average_entry_price": float(p.average_entry_price),
                    "current_price": float(ltp),
                    "market_value": float(mkt_val),
                    "unrealized_pnl": float(unreal_pnl),
                    "realized_pnl": float(p.realized_pnl),
                }
            )

        total_equity = account.available_cash + positions_val
        total_pnl = total_equity - account.initial_cash
        return_pct = round((total_pnl / account.initial_cash) * Decimal("100"), 2) if account.initial_cash > Decimal("0") else Decimal("0.00")

        return {
            "account_id": str(account.id),
            "account_name": account.name,
            "initial_cash": float(account.initial_cash),
            "available_cash": float(account.available_cash),
            "positions_value": float(positions_val),
            "total_equity": float(total_equity),
            "realized_pnl": float(realized_pnl),
            "unrealized_pnl": float(unrealized_pnl),
            "total_pnl": float(total_pnl),
            "return_pct": float(return_pct),
            "positions": pos_list,
            "disclaimer": "PAPER TRADING — SIMULATION ONLY — NO REAL MONEY OR BROKER EXECUTION",
        }
