from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, PaperPosition, PaperTradingAccount, User
from app.services.analytics.multi_portfolio_service import MultiPortfolioService


@pytest.mark.asyncio
async def test_multi_portfolio_aggregation_and_duplicates(db_session: AsyncSession) -> None:
    """Test multi-portfolio service aggregation, duplicate exposures, and attribution."""
    user = User(
        id=uuid4(),
        email=f"multi_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="Multi Tester",
    )
    db_session.add(user)
    await db_session.flush()

    # Portfolio A
    acct1 = PaperTradingAccount(
        id=uuid4(),
        user_id=user.id,
        name="Growth Portfolio",
        initial_cash=Decimal("1000000.00"),
        available_cash=Decimal("500000.00"),
        portfolio_type="PAPER",
    )
    # Portfolio B
    acct2 = PaperTradingAccount(
        id=uuid4(),
        user_id=user.id,
        name="Income Portfolio",
        initial_cash=Decimal("500000.00"),
        available_cash=Decimal("200000.00"),
        portfolio_type="PAPER",
    )
    db_session.add_all([acct1, acct2])

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

    # Overlapping position in both portfolios
    pos1 = PaperPosition(
        id=uuid4(),
        account_id=acct1.id,
        instrument_id=inst.id,
        quantity=Decimal("100.00"),
        average_entry_price=Decimal("2500.00"),
    )
    pos2 = PaperPosition(
        id=uuid4(),
        account_id=acct2.id,
        instrument_id=inst.id,
        quantity=Decimal("50.00"),
        average_entry_price=Decimal("2500.00"),
    )
    db_session.add_all([pos1, pos2])
    await db_session.commit()

    svc = MultiPortfolioService(db_session)

    # 1. Compare
    comp = await svc.compare_portfolios(user_id=user.id)
    assert len(comp) == 2

    # 2. Consolidated
    cons = await svc.get_consolidated_portfolio(user_id=user.id)
    assert cons["consolidated_summary"]["cash_balance"] == 700000.0
    assert "RELIANCE" in cons["consolidated_company_exposure_pct"]

    # 3. Duplicate Exposure Detection
    dups = await svc.detect_duplicate_exposures(user_id=user.id)
    assert len(dups) == 1
    assert dups[0]["symbol"] == "RELIANCE"
    assert dups[0]["portfolio_count"] == 2

    # 4. Attribution
    attr = await svc.get_portfolio_attribution(user_id=user.id)
    assert len(attr["attribution_by_portfolio"]) == 2


@pytest.mark.asyncio
async def test_multi_portfolio_api_endpoints(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test REST API endpoints for multi-portfolio management and consolidation."""
    # Create Portfolio
    res_create = await client.post(
        "/api/v1/portfolios",
        json={"name": "Secondary Trading Account", "initial_cash": 500000.0, "portfolio_type": "PAPER"},
        headers=auth_headers,
    )
    assert res_create.status_code == 200
    assert res_create.json()["name"] == "Secondary Trading Account"

    # List Portfolios
    res_list = await client.get("/api/v1/portfolios", headers=auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # Compare
    res_comp = await client.get("/api/v1/portfolios/compare", headers=auth_headers)
    assert res_comp.status_code == 200

    # Consolidated
    res_cons = await client.get("/api/v1/portfolios/consolidated", headers=auth_headers)
    assert res_cons.status_code == 200

    # Duplicate Exposures
    res_dup = await client.get("/api/v1/portfolios/consolidated/exposure", headers=auth_headers)
    assert res_dup.status_code == 200

    # Attribution
    res_attr = await client.get("/api/v1/portfolios/consolidated/attribution", headers=auth_headers)
    assert res_attr.status_code == 200
