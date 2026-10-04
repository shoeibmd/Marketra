from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, PaperOrder, PaperPosition, PaperTrade, PaperTradingAccount, User
from app.services.analytics.portfolio_analytics import PortfolioAnalyticsService


@pytest.mark.asyncio
async def test_portfolio_analytics_service_calculation(db_session: AsyncSession) -> None:
    """Test portfolio analytics service calculation for risk ratios and returns."""
    user = User(
        id=uuid4(),
        email=f"portfolio_test_{uuid4().hex[:6]}@example.com",
        hashed_password="hashed_pwd",
        full_name="Portfolio Tester",
    )
    db_session.add(user)
    await db_session.flush()

    account = PaperTradingAccount(
        id=uuid4(),
        user_id=user.id,
        initial_cash=Decimal("1000000.00"),
        available_cash=Decimal("500000.00"),
        portfolio_type="DEFAULT",
    )
    db_session.add(account)

    instrument = Instrument(
        id=uuid4(),
        symbol="RELIANCE",
        name="Reliance Industries Ltd",
        exchange_code="NSE",
        instrument_type="EQUITY",
        sector="Energy",
        currency="INR",
    )
    db_session.add(instrument)
    await db_session.flush()

    position = PaperPosition(
        id=uuid4(),
        account_id=account.id,
        instrument_id=instrument.id,
        quantity=Decimal("100.00"),
        average_entry_price=Decimal("2500.00"),
    )
    db_session.add(position)

    order = PaperOrder(
        id=uuid4(),
        account_id=account.id,
        instrument_id=instrument.id,
        side="BUY",
        quantity=Decimal("100.00"),
        status="EXECUTED",
    )
    db_session.add(order)
    await db_session.flush()

    trade = PaperTrade(
        id=uuid4(),
        account_id=account.id,
        order_id=order.id,
        instrument_id=instrument.id,
        side="BUY",
        quantity=Decimal("100.00"),
        execution_price=Decimal("2500.00"),
        realized_pnl=Decimal("25000.00"),
    )
    db_session.add(trade)
    await db_session.commit()

    svc = PortfolioAnalyticsService(db_session)
    res = await svc.generate_portfolio_analytics(user_id=user.id)

    assert res["summary"]["cash_balance"] == 500000.0
    assert res["summary"]["realized_pnl"] == 25000.0
    assert "risk_analytics" in res
    assert "max_drawdown_pct" in res["risk_analytics"]
    assert "performance_metrics" in res
    assert res["performance_metrics"]["win_rate_pct"] == 100.0
    assert res["performance_metrics"]["total_trades"] == 1


@pytest.mark.asyncio
async def test_portfolio_analytics_api_endpoint(client: AsyncClient, test_user: User, auth_headers: dict[str, str]) -> None:
    """Test API endpoint GET /api/v1/portfolio-analytics/summary."""
    res = await client.get("/api/v1/portfolio-analytics/summary", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "risk_analytics" in data
    assert "performance_metrics" in data
    assert "benchmark_comparison" in data
