import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import BrokerOrderMapping, ReconciliationRecord, User
from app.services.brokers.adapter import MockLiveBrokerAdapter, PaperBrokerAdapter

logger = logging.getLogger("terminal.reconciliation_service")


class ReconciliationService:
    """Service for comparing local order states against broker state and identifying discrepancies."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def reconcile_order(
        self,
        user: User,
        client_order_id: str,
    ) -> ReconciliationRecord:
        """Reconcile local BrokerOrderMapping with broker response state."""
        stmt = select(BrokerOrderMapping).where(
            BrokerOrderMapping.client_order_id == client_order_id,
            BrokerOrderMapping.user_id == user.id,
        )
        res = await self.db.execute(stmt)
        mapping = res.scalar_one_or_none()

        if not mapping:
            rec = ReconciliationRecord(
                id=uuid.uuid4(),
                user_id=user.id,
                client_order_id=client_order_id,
                broker_order_id=None,
                status="LOCAL_MISSING",
                discrepancy_details={"error": f"Client order ID {client_order_id} not found locally"},
            )
            self.db.add(rec)
            await self.db.commit()
            return rec

        if mapping.execution_mode == "PAPER":
            adapter = PaperBrokerAdapter(self.db)
        else:
            adapter = MockLiveBrokerAdapter(is_configured=True)

        if not mapping.broker_order_id:
            status_cat = "RECONCILIATION_REQUIRED"
            details = {"note": "Broker order ID is missing; submission status ambiguous"}
        else:
            broker_resp = await adapter.get_order_status(mapping.broker_order_id)
            broker_status = broker_resp.get("status", "UNKNOWN")

            if mapping.status == broker_status:
                status_cat = "MATCHED"
                details = {"local_status": mapping.status, "broker_status": broker_status}
            else:
                status_cat = "STATUS_MISMATCH"
                details = {"local_status": mapping.status, "broker_status": broker_status}

        rec = ReconciliationRecord(
            id=uuid.uuid4(),
            user_id=user.id,
            client_order_id=mapping.client_order_id,
            broker_order_id=mapping.broker_order_id,
            status=status_cat,
            discrepancy_details=details,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec
