import abc
import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, PaperTradingAccount, User
from app.services.paper.trading_engine import PaperTradingEngine

logger = logging.getLogger("terminal.broker_adapter")


class BaseBrokerAdapter(abc.ABC):
    """Abstract base class for broker adapters."""

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        """Return the unique provider name."""
        pass

    @abc.abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check connection health and return status dict."""
        pass

    @abc.abstractmethod
    async def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """Submit an order to the broker and return response."""
        pass

    @abc.abstractmethod
    async def cancel_order(self, broker_order_id: str) -> dict[str, Any]:
        """Cancel an open order."""
        pass

    @abc.abstractmethod
    async def get_order_status(self, broker_order_id: str) -> dict[str, Any]:
        """Fetch current order status."""
        pass


class PaperBrokerAdapter(BaseBrokerAdapter):
    """Paper trading broker adapter wrapping Phase 14 PaperTradingEngine."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.engine = PaperTradingEngine(db)

    def get_provider_name(self) -> str:
        return "PAPER_BROKER"

    async def health_check(self) -> dict[str, Any]:
        return {
            "provider_name": "PAPER_BROKER",
            "status": "HEALTHY",
            "execution_mode": "PAPER",
            "disclaimer": "PAPER TRADING SIMULATION — NO REAL BROKER OR LIVE ORDERS",
        }

    async def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        user: User = order_data["user"]
        inst: Instrument = order_data["instrument"]
        side: str = order_data["side"]
        quantity: Decimal = order_data["quantity"]
        order_type: str = order_data.get("order_type", "MARKET")
        requested_price: Decimal | None = order_data.get("requested_price")
        market_price: Decimal | None = order_data.get("market_price", Decimal("2450.00"))

        account = await self.engine.get_or_create_account(user)
        try:
            order = await self.engine.place_order(
                account=account,
                instrument=inst,
                side=side,
                quantity=quantity,
                order_type=order_type,
                requested_price=requested_price,
                market_price=market_price,
            )
            return {
                "client_order_id": order_data.get("client_order_id", str(order.id)),
                "broker_order_id": f"PAPER_{order.id}",
                "status": order.status,
                "executed_price": float(order.executed_price) if order.executed_price else None,
                "rejection_reason": order.rejection_reason,
            }
        except ValueError as e:
            return {
                "client_order_id": order_data.get("client_order_id", str(uuid.uuid4())),
                "broker_order_id": None,
                "status": "REJECTED",
                "rejection_reason": str(e),
            }

    async def cancel_order(self, broker_order_id: str) -> dict[str, Any]:
        return {"broker_order_id": broker_order_id, "status": "CANCELLED"}

    async def get_order_status(self, broker_order_id: str) -> dict[str, Any]:
        return {"broker_order_id": broker_order_id, "status": "FILLED"}


class MockLiveBrokerAdapter(BaseBrokerAdapter):
    """Sandbox simulation broker adapter for testing live order lifecycle. Explicitly marked SANDBOX / MOCK ONLY."""

    def __init__(self, is_configured: bool = False) -> None:
        self.is_configured = is_configured

    def get_provider_name(self) -> str:
        return "MOCK_LIVE_BROKER"

    async def health_check(self) -> dict[str, Any]:
        return {
            "provider_name": "MOCK_LIVE_BROKER",
            "status": "CONFIGURED" if self.is_configured else "NOT_CONFIGURED",
            "execution_mode": "SANDBOX_MOCK_LIVE",
            "disclaimer": "SANDBOX SIMULATION ONLY — NO REAL BROKER API KEY OR LIVE ORDERS",
        }

    async def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        if not self.is_configured:
            return {
                "client_order_id": order_data.get("client_order_id", str(uuid.uuid4())),
                "broker_order_id": None,
                "status": "REJECTED",
                "rejection_reason": "BROKER_NOT_CONFIGURED: Mock live broker credentials/environment not configured",
            }

        broker_id = f"MOCK_LIVE_{uuid.uuid4().hex[:8]}"
        exec_price = order_data.get("market_price", Decimal("2450.00"))

        return {
            "client_order_id": order_data.get("client_order_id", str(uuid.uuid4())),
            "broker_order_id": broker_id,
            "status": "FILLED",
            "executed_price": float(exec_price),
            "rejection_reason": None,
        }

    async def cancel_order(self, broker_order_id: str) -> dict[str, Any]:
        return {"broker_order_id": broker_order_id, "status": "CANCELLED"}

    async def get_order_status(self, broker_order_id: str) -> dict[str, Any]:
        return {"broker_order_id": broker_order_id, "status": "FILLED"}
