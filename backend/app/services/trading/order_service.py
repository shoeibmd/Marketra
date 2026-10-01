import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import BrokerOrderMapping, Instrument, TradingAuditLog, User
from app.services.brokers.adapter import MockLiveBrokerAdapter, PaperBrokerAdapter
from app.services.risk.risk_engine import RiskEngine

logger = logging.getLogger("terminal.order_service")


class OrderService:
    """Unified order management service enforcing state machine, idempotency, risk evaluation, and audit logging."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.risk_engine = RiskEngine(db)

    async def submit_order(
        self,
        user: User,
        instrument: Instrument,
        side: str,
        quantity: Decimal,
        execution_mode: str = "PAPER",
        order_type: str = "MARKET",
        requested_price: Decimal | None = None,
        market_price: Decimal | None = None,
        client_order_id: str | None = None,
    ) -> BrokerOrderMapping:
        """Process trading order through idempotency check, RiskEngine, broker adapter, and audit logging."""
        mode_clean = execution_mode.upper().strip()
        side_clean = side.upper().strip()
        client_id = client_order_id or f"ORD_{uuid.uuid4().hex[:12]}"

        # 1. Idempotency Check
        existing_stmt = select(BrokerOrderMapping).where(BrokerOrderMapping.client_order_id == client_id)
        existing_res = await self.db.execute(existing_stmt)
        existing_mapping = existing_res.scalar_one_or_none()

        if existing_mapping:
            logger.info(f"Idempotent order request received for client_order_id {client_id}. Returning existing record.")
            return existing_mapping

        # Create Order Record in CREATED state
        mapping = BrokerOrderMapping(
            id=uuid.uuid4(),
            client_order_id=client_id,
            user_id=user.id,
            instrument_id=instrument.id,
            execution_mode=mode_clean,
            side=side_clean,
            order_type=order_type.upper(),
            quantity=quantity,
            requested_price=requested_price,
            status="CREATED",
        )
        self.db.add(mapping)
        await self.db.commit()

        await self._log_audit(user.id, "ORDER_CREATED", mode_clean, client_id, {"side": side_clean, "quantity": float(quantity)})

        # 2. Risk Evaluation State
        mapping.status = "RISK_PENDING"
        await self.db.commit()

        effective_price = market_price if market_price else (requested_price if requested_price else Decimal("2450.00"))
        risk_passed, risk_reason = await self.risk_engine.evaluate_order_risk(
            user=user,
            instrument=instrument,
            side=side_clean,
            quantity=quantity,
            price=effective_price,
            execution_mode=mode_clean,
            client_order_id=client_id,
        )

        if not risk_passed:
            mapping.status = "RISK_REJECTED"
            mapping.rejection_reason = risk_reason
            await self.db.commit()
            await self._log_audit(user.id, "RISK_REJECTED", mode_clean, client_id, {"reason": risk_reason})
            return mapping

        # 3. Execution State & Broker Dispatch
        mapping.status = "SUBMITTING"
        await self.db.commit()

        order_payload = {
            "user": user,
            "instrument": instrument,
            "side": side_clean,
            "quantity": quantity,
            "order_type": order_type,
            "requested_price": requested_price,
            "market_price": effective_price,
            "client_order_id": client_id,
        }

        if mode_clean == "PAPER":
            adapter = PaperBrokerAdapter(self.db)
        else:
            adapter = MockLiveBrokerAdapter(is_configured=self.risk_engine.broker_configured)

        res = await adapter.place_order(order_payload)

        mapping.broker_order_id = res.get("broker_order_id")
        mapping.status = res.get("status", "REJECTED")
        mapping.rejection_reason = res.get("rejection_reason")
        if res.get("executed_price"):
            mapping.avg_executed_price = Decimal(str(res["executed_price"]))
            mapping.filled_quantity = quantity

        await self.db.commit()

        await self._log_audit(
            user.id,
            "BROKER_DISPATCH",
            mode_clean,
            client_id,
            {"status": mapping.status, "broker_order_id": mapping.broker_order_id, "rejection_reason": mapping.rejection_reason},
        )

        return mapping

    async def _log_audit(
        self,
        user_id: uuid.UUID,
        action: str,
        execution_mode: str,
        client_order_id: str,
        details: dict[str, Any],
    ) -> None:
        log = TradingAuditLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            execution_mode=execution_mode,
            client_order_id=client_order_id,
            details_json=details,
        )
        self.db.add(log)
        await self.db.commit()
