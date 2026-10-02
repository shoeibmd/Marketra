import logging
import os
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, RiskDecision, RiskLimit, User

logger = logging.getLogger("terminal.risk_engine")


class RiskEngine:
    """Independent pre-trade risk engine and live trading safety gate."""

    _STAGE_A_LIVE_ENABLED: bool | None = None
    _STAGE_B_KILL_SWITCH: bool | None = None

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

        # Environment Safety Gate Defaults or Runtime Overrides
        if RiskEngine._STAGE_A_LIVE_ENABLED is not None:
            self.live_trading_enabled = RiskEngine._STAGE_A_LIVE_ENABLED
        else:
            self.live_trading_enabled = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"

        if RiskEngine._STAGE_B_KILL_SWITCH is not None:
            self.trading_kill_switch = RiskEngine._STAGE_B_KILL_SWITCH
        else:
            self.trading_kill_switch = os.getenv("TRADING_KILL_SWITCH", "true").lower() == "true"

        self.risk_engine_enabled = os.getenv("RISK_ENGINE_ENABLED", "true").lower() == "true"
        self.broker_configured = os.getenv("BROKER_CONFIGURED", "false").lower() == "true"

    async def get_or_create_user_risk_limits(self, user: User) -> RiskLimit:
        """Get or initialize user-configurable risk limits."""
        stmt = select(RiskLimit).where(RiskLimit.user_id == user.id)
        res = await self.db.execute(stmt)
        limits = res.scalar_one_or_none()

        if not limits:
            limits = RiskLimit(
                id=uuid.uuid4(),
                user_id=user.id,
                max_order_quantity=Decimal("10000"),
                max_order_value=Decimal("250000.00"),
                max_portfolio_exposure_pct=Decimal("80.00"),
                daily_loss_limit=Decimal("50000.00"),
                max_open_orders=20,
            )
            self.db.add(limits)
            await self.db.commit()
            await self.db.refresh(limits)

        return limits

    async def evaluate_order_risk(
        self,
        user: User,
        instrument: Instrument,
        side: str,
        quantity: Decimal,
        price: Decimal,
        execution_mode: str = "PAPER",
        client_order_id: str | None = None,
    ) -> tuple[bool, str]:
        """Evaluate pre-trade risk rules and server-side live safety gate."""
        order_ref = client_order_id or str(uuid.uuid4())

        # 1. Server-Side Live Safety Gate Check
        if execution_mode.upper() == "LIVE":
            if not self.live_trading_enabled:
                await self._record_decision(user.id, order_ref, "LIVE_SAFETY_GATE", "LIVE", "DISABLED", "REJECTED", "LIVE_TRADING_DISABLED: Live trading environment flag is set to false")
                return False, "LIVE_TRADING_DISABLED: Live trading is disabled on server"

            if self.trading_kill_switch:
                await self._record_decision(user.id, order_ref, "LIVE_SAFETY_GATE", "ACTIVE", "INACTIVE", "REJECTED", "KILL_SWITCH_ACTIVE: Emergency kill switch is active")
                return False, "KILL_SWITCH_ACTIVE: Live trading emergency kill switch is active"

            if not self.broker_configured:
                await self._record_decision(user.id, order_ref, "LIVE_SAFETY_GATE", "NOT_CONFIGURED", "CONFIGURED", "REJECTED", "BROKER_NOT_CONFIGURED: Production broker API credentials not configured")
                return False, "BROKER_NOT_CONFIGURED: Broker credentials not configured"

        if not self.risk_engine_enabled:
            await self._record_decision(user.id, order_ref, "RISK_ENGINE_GATE", "DISABLED", "ENABLED", "REJECTED", "RISK_ENGINE_DISABLED: Risk Engine must be enabled to process live orders")
            return False, "RISK_ENGINE_DISABLED: Pre-trade risk engine disabled"

        # Fetch configured limits
        limits = await self.get_or_create_user_risk_limits(user)

        # 2. Rule: Symbol Status
        if not instrument.is_active:
            reason = f"SYMBOL_INACTIVE: Instrument {instrument.symbol} is inactive or delisted"
            await self._record_decision(user.id, order_ref, "SYMBOL_STATUS", instrument.symbol, "ACTIVE", "REJECTED", reason)
            return False, reason

        # 3. Rule: Max Order Quantity
        if quantity > limits.max_order_quantity:
            reason = f"MAX_ORDER_QUANTITY_EXCEEDED: Requested quantity {quantity} exceeds limit {limits.max_order_quantity}"
            await self._record_decision(user.id, order_ref, "MAX_ORDER_QUANTITY", str(quantity), str(limits.max_order_quantity), "REJECTED", reason)
            return False, reason

        # 4. Rule: Max Order Value
        order_val = round(quantity * price, 2)
        if order_val > limits.max_order_value:
            reason = f"MAX_ORDER_VALUE_EXCEEDED: Requested value ₹{order_val} exceeds limit ₹{limits.max_order_value}"
            await self._record_decision(user.id, order_ref, "MAX_ORDER_VALUE", f"₹{order_val}", f"₹{limits.max_order_value}", "REJECTED", reason)
            return False, reason

        # All Risk Checks Passed
        await self._record_decision(user.id, order_ref, "ALL_RISK_RULES", f"₹{order_val}", "PASS", "APPROVED", "Risk validation passed")
        return True, "APPROVED"

    async def _record_decision(
        self,
        user_id: uuid.UUID,
        client_order_id: str,
        rule_name: str,
        input_value: str,
        threshold_value: str,
        decision: str,
        reason: str,
    ) -> None:
        dec = RiskDecision(
            id=uuid.uuid4(),
            user_id=user_id,
            client_order_id=client_order_id,
            rule_name=rule_name,
            input_value=input_value,
            threshold_value=threshold_value,
            decision=decision,
            reason=reason,
        )
        self.db.add(dec)
        await self.db.commit()
