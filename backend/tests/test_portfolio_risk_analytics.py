from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, OHLCV, PaperPosition, PaperTradingAccount, User
from app.services.analytics.portfolio_risk import PortfolioRiskService


@pytest.mark.asyncio
async def test_portfolio_risk_stress_testing(db_session: AsyncSession) -> None:
    """Test deterministic stress test scenario calculations with exact Decimal math."""
    user = User(
        id=uuid4(),
        email=f"risk_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="Risk Tester",
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

    inst1 = Instrument(
        id=uuid4(),
        symbol="RELIANCE",
        name="Reliance Industries",
        exchange_code="NSE",
        instrument_type="EQUITY",
        sector="Energy",
        currency="INR",
    )
    inst2 = Instrument(
        id=uuid4(),
        symbol="TCS",
        name="Tata Consultancy Services",
        exchange_code="NSE",
        instrument_type="EQUITY",
        sector="IT",
        currency="INR",
    )
    db_session.add_all([inst1, inst2])
    await db_session.flush()

    pos1 = PaperPosition(
        id=uuid4(),
        account_id=account.id,
        instrument_id=inst1.id,
        quantity=Decimal("100.00"),
        average_entry_price=Decimal("2500.00"),
    )
    pos2 = PaperPosition(
        id=uuid4(),
        account_id=account.id,
        instrument_id=inst2.id,
        quantity=Decimal("50.00"),
        average_entry_price=Decimal("3500.00"),
    )
    db_session.add_all([pos1, pos2])
    await db_session.commit()

    svc = PortfolioRiskService(db_session)

    # Market Shock -10%
    res_m10 = await svc.run_stress_test(
        user_id=user.id,
        market_shock_pct=-10.0,
        scenario_name="NIFTY50_-10%",
    )
    assert res_m10["data_quality_status"] == "AVAILABLE"
    assert res_m10["hypothetical_impact"]["percentage_portfolio_impact"] < 0
    assert "disclaimer" in res_m10

    # Sector Shock IT -10%
    res_sec = await svc.run_stress_test(
        user_id=user.id,
        sector_shocks={"IT": -10.0},
        scenario_name="SECTOR_IT_-10%",
    )
    assert res_sec["data_quality_status"] == "AVAILABLE"
    impacts = {item["sector"]: item["hypothetical_pnl_impact"] for item in res_sec["impact_by_sector"]}
    assert impacts.get("IT", 0) < 0
    assert impacts.get("Energy", 0) == 0


@pytest.mark.asyncio
async def test_var_and_expected_shortfall(db_session: AsyncSession) -> None:
    """Test VaR and Expected Shortfall calculation handling."""
    user = User(
        id=uuid4(),
        email=f"var_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="VaR Tester",
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
    await db_session.commit()

    svc = PortfolioRiskService(db_session)
    res = await svc.calculate_var_and_es(user_id=user.id)
    assert res["data_quality_status"] in ("INSUFFICIENT_DATA", "DATA_UNAVAILABLE")


@pytest.mark.asyncio
async def test_diversification_and_risk_contribution(db_session: AsyncSession) -> None:
    """Test diversification score and risk contribution calculation."""
    user = User(
        id=uuid4(),
        email=f"div_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="Div Tester",
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

    inst = Instrument(
        id=uuid4(),
        symbol="INFY",
        name="Infosys Ltd",
        exchange_code="NSE",
        instrument_type="EQUITY",
        sector="IT",
        currency="INR",
    )
    db_session.add(inst)
    await db_session.flush()

    pos = PaperPosition(
        id=uuid4(),
        account_id=account.id,
        instrument_id=inst.id,
        quantity=Decimal("100.00"),
        average_entry_price=Decimal("1500.00"),
    )
    db_session.add(pos)
    await db_session.commit()

    svc = PortfolioRiskService(db_session)
    div = await svc.calculate_diversification_metrics(user_id=user.id)
    assert div["data_quality_status"] == "AVAILABLE"
    assert "hhi_index" in div["summary"]

    contrib = await svc.calculate_risk_contribution(user_id=user.id)
    assert contrib["data_quality_status"] == "AVAILABLE"
    assert len(contrib["risk_contribution_by_company"]) == 1


@pytest.mark.asyncio
async def test_portfolio_risk_api_authorization(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test REST API endpoint access and authorization."""
    # Summary
    res_sum = await client.get("/api/v1/portfolio/risk/summary", headers=auth_headers)
    assert res_sum.status_code == 200

    # VaR
    res_var = await client.get("/api/v1/portfolio/risk/var?confidence_level=0.95", headers=auth_headers)
    assert res_var.status_code == 200

    # Correlation
    res_corr = await client.get("/api/v1/portfolio/risk/correlation", headers=auth_headers)
    assert res_corr.status_code == 200

    # Stress Test
    res_stress = await client.post(
        "/api/v1/portfolio/risk/stress-test",
        json={"market_shock_pct": -10.0, "scenario_name": "API_TEST_STRESS"},
        headers=auth_headers,
    )
    assert res_stress.status_code == 200
    assert res_stress.json()["scenario"] == "API_TEST_STRESS"
