import uuid
from decimal import Decimal
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.domain import User, Instrument, PaperTradingAccount
from app.core.auth.jwt_handler import create_access_token
from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.services.paper.trading_engine import PaperTradingEngine
from app.services.paper.backtest_engine import StrategyRegistry


class MockAsyncSession:
    """Mock async session for paper trading unit testing."""

    def __init__(self) -> None:
        self.added: list[object] = []
        self.deleted: list[object] = []
        self.accounts: list[PaperTradingAccount] = []

    def add(self, instance: object) -> None:
        self.added.append(instance)
        if isinstance(instance, PaperTradingAccount):
            self.accounts.append(instance)

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
        return self.session.accounts[0] if self.session.accounts else None


def test_strategy_registry_security() -> None:
    # Verify only pre-built, trusted server-side strategies exist
    strategies = StrategyRegistry.get_supported_strategies()
    names = [s["name"] for s in strategies]
    assert "SMA_CROSSOVER" in names
    assert "EVENT_REACTION_RESEARCH" in names
    # Prohibit un-sanctioned dynamic code
    assert "CUSTOM_CODE" not in names


@pytest.mark.asyncio
async def test_paper_trading_execution_flow() -> None:
    u1 = User(id=uuid.uuid4(), email="trader1@terminal.local", hashed_password="hash", full_name="Trader One")
    u2 = User(id=uuid.uuid4(), email="trader2@terminal.local", hashed_password="hash", full_name="Trader Two")

    mock_db = MockAsyncSession()

    engine = PaperTradingEngine(mock_db)  # type: ignore[arg-type]
    account = await engine.get_or_create_account(u1, initial_cash=Decimal("100000.00"))

    assert account.initial_cash == Decimal("100000.00")
    assert account.available_cash == Decimal("100000.00")

    inst = Instrument(id=uuid.uuid4(), symbol="RELIANCE", name="Reliance Industries Ltd", exchange_code="NSE", instrument_type="EQUITY")

    # 1. Place BUY Order
    order_buy = await engine.place_order(
        account=account,
        instrument=inst,
        side="BUY",
        quantity=Decimal("10"),
        market_price=Decimal("2000.00"),
        fee_amount=Decimal("20.00"),
        slippage_pct=Decimal("0.00"),
    )

    assert order_buy.status == "EXECUTED"
    # Cost = 10 * 2000 + 20 = 20020. Available cash = 100000 - 20020 = 79980
    assert account.available_cash == Decimal("79980.00")

    # 2. Reject BUY on insufficient cash
    with pytest.raises(ValueError, match="INSUFFICIENT_CASH"):
        await engine.place_order(
            account=account,
            instrument=inst,
            side="BUY",
            quantity=Decimal("1000"),
            market_price=Decimal("2000.00"),
        )

    # 3. Reject SELL on insufficient holdings
    inst_other = Instrument(id=uuid.uuid4(), symbol="TCS", name="Tata Consultancy Services", exchange_code="NSE", instrument_type="EQUITY")
    order_reject_sell = await engine.place_order(
        account=account,
        instrument=inst_other,
        side="SELL",
        quantity=Decimal("5"),
        market_price=Decimal("3000.00"),
    )
    assert order_reject_sell.status == "REJECTED"
    assert "INSUFFICIENT_POSITION" in str(order_reject_sell.rejection_reason)


@pytest.mark.asyncio
async def test_paper_trading_api_endpoints() -> None:
    u1 = User(id=uuid.uuid4(), email="trader1@terminal.local", hashed_password="hash", full_name="Trader One")
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
            # 1. Get paper account
            res_acc = await ac.get("/api/v1/paper/accounts/me", headers=headers1)
            assert res_acc.status_code == 200
            data_acc = res_acc.json()
            assert "available_cash" in data_acc
            assert "PAPER TRADING — SIMULATION ONLY" in data_acc["disclaimer"]

            # 2. List strategies
            res_strats = await ac.get("/api/v1/paper/strategies", headers=headers1)
            assert res_strats.status_code == 200
            assert len(res_strats.json()) >= 2

            # 3. Reject unsanctioned code execution strategy
            res_bad_strat = await ac.post(
                "/api/v1/paper/backtests",
                json={"strategy_name": "MALICIOUS_EVAL", "symbol": "RELIANCE"},
                headers=headers1,
            )
            assert res_bad_strat.status_code == 400
            assert "Unsupported strategy" in res_bad_strat.json()["detail"]
    finally:
        app.dependency_overrides.clear()
