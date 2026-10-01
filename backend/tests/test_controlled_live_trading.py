import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.domain import User, Instrument, OrderConfirmation, LiveTradingActivationLog
from app.core.auth.jwt_handler import create_access_token
from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.services.trading.activation_service import LiveTradingActivationService
from app.services.trading.confirmation_service import ConfirmationService
from app.services.trading.reconciliation_service import ReconciliationService


class MockAsyncSession:
    """Mock async session for controlled live trading unit testing."""

    def __init__(self) -> None:
        self.added: list[object] = []
        self.confirmations: list[OrderConfirmation] = []

    def add(self, instance: object) -> None:
        self.added.append(instance)
        if isinstance(instance, OrderConfirmation):
            self.confirmations.append(instance)

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
        return self.session.confirmations[0] if self.session.confirmations else None


@pytest.mark.asyncio
async def test_two_stage_live_activation() -> None:
    admin_user = User(id=uuid.uuid4(), email="admin@terminal.local", hashed_password="hash", full_name="Admin", role="admin")
    regular_user = User(id=uuid.uuid4(), email="user@terminal.local", hashed_password="hash", full_name="User", role="user")

    mock_db = MockAsyncSession()
    service = LiveTradingActivationService(mock_db)  # type: ignore[arg-type]

    # 1. Non-admin user cannot activate live trading
    with pytest.raises(ValueError, match="USER_NOT_AUTHORIZED"):
        await service.update_live_activation_stage(
            admin_user=regular_user,
            stage="STAGE_A",
            enable=True,
            reason="Attempting unauthorized activation",
        )

    # 2. Admin user can update Stage A
    res_stage_a = await service.update_live_activation_stage(
        admin_user=admin_user,
        stage="STAGE_A",
        enable=True,
        reason="Enabling Stage A for testing",
    )
    assert res_stage_a["status"] == "SUCCESS"
    assert res_stage_a["current_state"]["live_trading_enabled"] is True


@pytest.mark.asyncio
async def test_order_confirmation_token_security() -> None:
    u1 = User(id=uuid.uuid4(), email="trader@terminal.local", hashed_password="hash", full_name="Trader")
    mock_db = MockAsyncSession()
    service = ConfirmationService(mock_db)  # type: ignore[arg-type]

    order_params = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "order_type": "MARKET",
        "requested_price": 2000.0,
        "execution_mode": "LIVE",
    }

    # 1. Create confirmation token
    conf = await service.create_confirmation(u1, "ORD_TEST_1001", order_params, ttl_minutes=5)
    assert conf.confirmation_token.startswith("CONF_")
    assert conf.is_used is False

    # 2. Validate with modified order parameter (quantity changed 10 -> 20)
    modified_params = dict(order_params)
    modified_params["quantity"] = 20

    valid_mod, reason_mod = await service.validate_and_consume_confirmation(
        user=u1,
        confirmation_token=conf.confirmation_token,
        current_order_params=modified_params,
    )
    assert valid_mod is False
    assert "CONFIRMATION_PARAMETER_MISMATCH" in reason_mod

    # 3. Validate with exact matching parameters
    valid_exact, reason_exact = await service.validate_and_consume_confirmation(
        user=u1,
        confirmation_token=conf.confirmation_token,
        current_order_params=order_params,
    )
    assert valid_exact is True
    assert conf.is_used is True

    # 4. Cannot re-use consumed token
    valid_reuse, reason_reuse = await service.validate_and_consume_confirmation(
        user=u1,
        confirmation_token=conf.confirmation_token,
        current_order_params=order_params,
    )
    assert valid_reuse is False
    assert "CONFIRMATION_ALREADY_USED" in reason_reuse


@pytest.mark.asyncio
async def test_reconciliation_and_admin_apis() -> None:
    admin_user = User(id=uuid.uuid4(), email="admin@terminal.local", hashed_password="hash", full_name="Admin", role="admin")
    token_admin = create_access_token({"sub": admin_user.email})
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    mock_db = MockAsyncSession()

    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Admin Live Activation endpoint
            res_act = await ac.post(
                "/api/v1/admin/live-trading/activate",
                json={"stage": "STAGE_A", "enable": True, "reason": "Admin test activation"},
                headers=headers_admin,
            )
            assert res_act.status_code == 200
            assert res_act.json()["status"] == "SUCCESS"

            # 2. List reconciliation records
            res_rec = await ac.get("/api/v1/reconciliation", headers=headers_admin)
            assert res_rec.status_code == 200
            assert isinstance(res_rec.json(), list)
    finally:
        app.dependency_overrides.clear()
