from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, PaperPosition, PaperTradingAccount, User
from app.services.analytics.portfolio_risk_command_center import PortfolioRiskCommandCenterService


@pytest.mark.asyncio
async def test_command_center_service_aggregation(db_session: AsyncSession) -> None:
    """Test Command Center consolidation service output and report export."""
    user = User(
        id=uuid4(),
        email=f"cmd_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="Command Center Tester",
    )
    db_session.add(user)
    await db_session.flush()

    account = PaperTradingAccount(
        id=uuid4(),
        user_id=user.id,
        initial_cash=Decimal("1000000.00"),
        available_cash=Decimal("600000.00"),
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

    pos = PaperPosition(
        id=uuid4(),
        account_id=account.id,
        instrument_id=inst.id,
        quantity=Decimal("100.00"),
        average_entry_price=Decimal("2500.00"),
    )
    db_session.add(pos)
    await db_session.commit()

    svc = PortfolioRiskCommandCenterService(db_session)

    # 1. Test Aggregation
    data = await svc.get_command_center_data(user_id=user.id)
    assert "executive_summary" in data
    assert data["executive_summary"]["portfolio_value"] > 0
    assert "performance_vs_benchmark" in data
    assert "NIFTY50" in str(data["performance_vs_benchmark"]) or "nifty50_return_pct" in str(data["performance_vs_benchmark"])

    # 2. Test Report Export
    report = await svc.generate_exportable_risk_report(user_id=user.id)
    assert "markdown_content" in report
    assert "Analytical information only" in report["markdown_content"]


@pytest.mark.asyncio
async def test_command_center_api_endpoints(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test Command Center API endpoints and authorization."""
    # Command Center Data
    res = await client.get("/api/v1/portfolio/risk-command-center", headers=auth_headers)
    assert res.status_code == 200
    assert "executive_summary" in res.json()

    # History
    res_hist = await client.get("/api/v1/portfolio/risk-command-center/history", headers=auth_headers)
    assert res_hist.status_code == 200

    # Export Report
    res_exp = await client.get("/api/v1/portfolio/risk-command-center/export", headers=auth_headers)
    assert res_exp.status_code == 200
    assert "markdown_content" in res_exp.json()
