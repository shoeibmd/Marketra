from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, PaperPosition, PaperTradingAccount, User
from app.services.analytics.portfolio_briefing_service import PortfolioBriefingService
from app.services.analytics.portfolio_change_detection import PortfolioChangeDetectionService


@pytest.mark.asyncio
async def test_portfolio_change_detection(db_session: AsyncSession) -> None:
    """Test change detection engine generating PortfolioChangeEvent records."""
    user = User(
        id=uuid4(),
        email=f"change_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="Change Tester",
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
        symbol="TCS",
        name="Tata Consultancy Services",
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
        average_entry_price=Decimal("3500.00"),
    )
    db_session.add(pos)
    await db_session.commit()

    change_svc = PortfolioChangeDetectionService(db_session)
    changes = await change_svc.detect_and_record_changes(user_id=user.id)
    assert isinstance(changes, list)


@pytest.mark.asyncio
async def test_portfolio_briefing_generation(db_session: AsyncSession) -> None:
    """Test PortfolioBriefingService generating structured Daily and Weekly briefings."""
    user = User(
        id=uuid4(),
        email=f"briefing_tester_{uuid4().hex[:6]}@example.com",
        hashed_password="pwd",
        full_name="Briefing Tester",
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

    briefing_svc = PortfolioBriefingService(db_session)

    # Daily Briefing
    daily_b = await briefing_svc.generate_briefing(user_id=user.id, briefing_type="DAILY")
    assert daily_b.briefing_type == "DAILY"
    assert daily_b.status in ("COMPLETED", "PARTIAL")
    assert "portfolio_summary" in daily_b.content_json

    # Weekly Briefing
    weekly_b = await briefing_svc.generate_briefing(user_id=user.id, briefing_type="WEEKLY")
    assert weekly_b.briefing_type == "WEEKLY"


@pytest.mark.asyncio
async def test_portfolio_briefing_api_endpoints(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test REST API endpoints for briefings, preferences, and changes timeline."""
    # Generate On-Demand
    res_gen = await client.post(
        "/api/v1/portfolio/briefings/generate",
        json={"briefing_type": "DAILY"},
        headers=auth_headers,
    )
    assert res_gen.status_code == 200
    briefing_id = res_gen.json()["briefing_id"]

    # Get Briefings List
    res_list = await client.get("/api/v1/portfolio/briefings", headers=auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # Get Briefing Detail
    res_detail = await client.get(f"/api/v1/portfolio/briefings/{briefing_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == briefing_id

    # Get Changes Timeline
    res_changes = await client.get("/api/v1/portfolio/briefings/changes", headers=auth_headers)
    assert res_changes.status_code == 200

    # Get Preferences
    res_pref = await client.get("/api/v1/portfolio/briefings/preferences", headers=auth_headers)
    assert res_pref.status_code == 200
    assert res_pref.json()["daily_briefing_enabled"] is True
