from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, PaperPosition, PaperTradingAccount, User
from app.services.analytics.portfolio_risk_monitoring import PortfolioRiskMonitoringService


@pytest.mark.asyncio
async def test_risk_monitoring_service_evaluation_and_recovery(db_session: AsyncSession) -> None:
    """Test risk monitoring evaluation, state machine transitions, cooldown suppression, and recovery detection."""
    user = User(
        id=uuid4(),
        email=f"alert_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="Alert Tester",
    )
    db_session.add(user)
    await db_session.flush()

    account = PaperTradingAccount(
        id=uuid4(),
        user_id=user.id,
        initial_cash=Decimal("1000000.00"),
        available_cash=Decimal("200000.00"),  # High positions concentration
        portfolio_type="DEFAULT",
    )
    db_session.add(account)

    inst = Instrument(
        id=uuid4(),
        symbol="RELIANCE",
        name="Reliance Industries",
        exchange_code="NSE",
        instrument_type="EQUITY",
        sector="Energy",
        currency="INR",
    )
    db_session.add(inst)
    await db_session.flush()

    # Create 80% concentrated position in single stock
    pos = PaperPosition(
        id=uuid4(),
        account_id=account.id,
        instrument_id=inst.id,
        quantity=Decimal("300.00"),
        average_entry_price=Decimal("2500.00"),
    )
    db_session.add(pos)
    await db_session.commit()

    svc = PortfolioRiskMonitoringService(db_session)

    # 1. Initial Evaluation -> Should Trigger Concentration Alerts
    triggered = await svc.evaluate_user_portfolio_risk(user_id=user.id)
    assert len(triggered) >= 1
    alert = triggered[0]
    assert alert.status == "TRIGGERED"
    assert alert.user_id == user.id

    # 2. Immediate Second Evaluation -> Cooldown Suppression
    triggered_again = await svc.evaluate_user_portfolio_risk(user_id=user.id)
    assert len(triggered_again) == 0

    # 3. Reduce position -> Recovery Detection
    pos.quantity = Decimal("10.00")  # Position now tiny fraction of portfolio
    await db_session.commit()

    eval_recovered = await svc.evaluate_user_portfolio_risk(user_id=user.id)
    # Service generates recovery records when transitioning state back to NORMAL
    assert any(a.alert_type == "PORTFOLIO_RISK_RECOVERED" or a.status == "RECOVERED" for a in eval_recovered)


@pytest.mark.asyncio
async def test_risk_alert_preferences_crud(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test risk alert preferences GET, PUT, and RESET endpoints."""
    # Get Preferences
    res_get = await client.get("/api/v1/portfolio/risk/alerts/preferences", headers=auth_headers)
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["drawdown_threshold_pct"] == 5.0

    # Update Preferences
    res_put = await client.put(
        "/api/v1/portfolio/risk/alerts/preferences",
        json={"drawdown_threshold_pct": 12.5, "company_concentration_threshold_pct": 35.0},
        headers=auth_headers,
    )
    assert res_put.status_code == 200
    assert res_put.json()["drawdown_threshold_pct"] == 12.5

    # Reset Preferences
    res_reset = await client.post("/api/v1/portfolio/risk/alerts/preferences/reset", headers=auth_headers)
    assert res_reset.status_code == 200
    assert res_reset.json()["drawdown_threshold_pct"] == 5.0


@pytest.mark.asyncio
async def test_risk_alerts_and_test_endpoint(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test on-demand evaluation test endpoint and active risk alerts fetching."""
    # Trigger test evaluation
    res_test = await client.post("/api/v1/portfolio/risk/alerts/test", headers=auth_headers)
    assert res_test.status_code == 200
    assert res_test.json()["status"] == "completed"

    # Get Active Risk Alerts
    res_alerts = await client.get("/api/v1/portfolio/risk/alerts/active", headers=auth_headers)
    assert res_alerts.status_code == 200
    assert isinstance(res_alerts.json(), list)
