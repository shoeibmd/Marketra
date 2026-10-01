import uuid
from decimal import Decimal
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.domain import User, Instrument
from app.core.auth.jwt_handler import create_access_token
from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.services.brokers.adapter import PaperBrokerAdapter, MockLiveBrokerAdapter
from app.services.risk.risk_engine import RiskEngine
from app.services.trading.order_service import OrderService


class MockAsyncSession:
    """Mock async session for risk and broker integration unit testing."""

    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, instance: object) -> None:
        self.added.append(instance)

    async def commit(self) -> None:
        pass

    async def refresh(self, instance: object) -> None:
        pass

    async def execute(self, stmt: object) -> "MockResult":
        return MockResult(self)


class MockResult:

    def __init__(self, session: MockAsyncSession) -> None:
        self.session = session

    def scalars(self) -> "MockResult":
        return self

    def all(self) -> list[object]:
        return []

    def scalar_one_or_none(self) -> object | None:
        return None


@pytest.mark.asyncio
async def test_live_trading_safety_gate() -> None:
    u1 = User(id=uuid.uuid4(), email="riskuser@terminal.local", hashed_password="hash", full_name="Risk User")
    inst = Instrument(id=uuid.uuid4(), symbol="RELIANCE", name="Reliance Industries Ltd", exchange_code="NSE", instrument_type="EQUITY", is_active=True)

    mock_db = MockAsyncSession()
    risk = RiskEngine(mock_db)  # type: ignore[arg-type]

    # Verify default production safety flags
    assert risk.live_trading_enabled is False
    assert risk.trading_kill_switch is True

    # Attempt LIVE order when LIVE_TRADING_ENABLED=false
    passed, reason = await risk.evaluate_order_risk(
        user=u1,
        instrument=inst,
        side="BUY",
        quantity=Decimal("10"),
        price=Decimal("2000.00"),
        execution_mode="LIVE",
    )
    assert passed is False
    assert "LIVE_TRADING_DISABLED" in reason


@pytest.mark.asyncio
async def test_pre_trade_risk_rules() -> None:
    u1 = User(id=uuid.uuid4(), email="riskuser@terminal.local", hashed_password="hash", full_name="Risk User")
    inst = Instrument(id=uuid.uuid4(), symbol="RELIANCE", name="Reliance Industries Ltd", exchange_code="NSE", instrument_type="EQUITY", is_active=True)

    mock_db = MockAsyncSession()
    risk = RiskEngine(mock_db)  # type: ignore[arg-type]

    # 1. Rule: Max Order Value Exceeded (₹3,00,000 exceeds ₹2,50,000 limit)
    passed_val, reason_val = await risk.evaluate_order_risk(
        user=u1,
        instrument=inst,
        side="BUY",
        quantity=Decimal("150"),
        price=Decimal("2000.00"),
        execution_mode="PAPER",
    )
    assert passed_val is False
    assert "MAX_ORDER_VALUE_EXCEEDED" in reason_val

    # 2. Rule: Max Order Quantity Exceeded (15,000 exceeds 10,000 limit)
    passed_qty, reason_qty = await risk.evaluate_order_risk(
        user=u1,
        instrument=inst,
        side="BUY",
        quantity=Decimal("15000"),
        price=Decimal("10.00"),
        execution_mode="PAPER",
    )
    assert passed_qty is False
    assert "MAX_ORDER_QUANTITY_EXCEEDED" in reason_qty

    # 3. Rule: Inactive Symbol
    inst_inactive = Instrument(id=uuid.uuid4(), symbol="DELISTED", name="Delisted Co", exchange_code="NSE", instrument_type="EQUITY", is_active=False)
    passed_inact, reason_inact = await risk.evaluate_order_risk(
        user=u1,
        instrument=inst_inactive,
        side="BUY",
        quantity=Decimal("10"),
        price=Decimal("100.00"),
        execution_mode="PAPER",
    )
    assert passed_inact is False
    assert "SYMBOL_INACTIVE" in reason_inact


@pytest.mark.asyncio
async def test_trading_and_broker_rest_apis() -> None:
    u1 = User(id=uuid.uuid4(), email="trader@terminal.local", hashed_password="hash", full_name="Trader")
    token1 = create_access_token({"sub": u1.email})
    headers1 = {"Authorization": f"Bearer {token1}"}

    mock_db = MockAsyncSession()

    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return u1

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Broker adapters list
            res_brokers = await ac.get("/api/v1/brokers")
            assert res_brokers.status_code == 200
            brokers = res_brokers.json()
            assert len(brokers) >= 2

            # 2. Paper broker health
            res_paper_health = await ac.get("/api/v1/brokers/PAPER_BROKER/health")
            assert res_paper_health.status_code == 200
            assert res_paper_health.json()["provider_name"] == "PAPER_BROKER"

            # 3. Risk Engine status
            res_risk_st = await ac.get("/api/v1/risk/status")
            assert res_risk_st.status_code == 200
            assert res_risk_st.json()["live_trading_enabled"] is False

            # 4. User risk limits
            res_limits = await ac.get("/api/v1/risk/limits", headers=headers1)
            assert res_limits.status_code == 200
            assert "max_order_value" in res_limits.json()
    finally:
        app.dependency_overrides.clear()
