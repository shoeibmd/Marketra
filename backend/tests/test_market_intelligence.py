from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Instrument, User
from app.services.analytics.market_intelligence_service import MarketIntelligenceService


@pytest.mark.asyncio
async def test_market_intelligence_overview_and_breadth(db_session: AsyncSession) -> None:
    """Test MarketIntelligenceService calculating market overview and breadth analytics."""
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
    await db_session.commit()

    svc = MarketIntelligenceService(db_session)
    overview = await svc.get_market_overview_and_breadth()
    assert "market_breadth" in overview
    assert "advance_decline_ratio" in overview["market_breadth"]


@pytest.mark.asyncio
async def test_sector_intelligence_and_regime(db_session: AsyncSession) -> None:
    """Test sector performance matrix, sector correlation, and market regime classification."""
    svc = MarketIntelligenceService(db_session)

    # Sectors
    sectors = await svc.get_sector_intelligence()
    assert "sector_performance" in sectors
    assert "sector_correlation_matrix" in sectors

    # Regime
    regime = await svc.get_market_regime()
    assert "regime_classification" in regime
    assert regime["data_quality_status"] == "AVAILABLE"


@pytest.mark.asyncio
async def test_market_anomalies_detection(db_session: AsyncSession) -> None:
    """Test statistical anomaly detection engine."""
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
    await db_session.commit()

    svc = MarketIntelligenceService(db_session)
    anomalies = await svc.detect_market_anomalies()
    assert isinstance(anomalies, list)


@pytest.mark.asyncio
async def test_market_intelligence_api_endpoints(client: AsyncClient) -> None:
    """Test Market Intelligence public REST API endpoints."""
    # Overview
    res_ov = await client.get("/api/v1/market-intelligence/overview")
    assert res_ov.status_code == 200

    # Breadth
    res_br = await client.get("/api/v1/market-intelligence/breadth")
    assert res_br.status_code == 200

    # Sectors
    res_sec = await client.get("/api/v1/market-intelligence/sectors")
    assert res_sec.status_code == 200

    # Regime
    res_reg = await client.get("/api/v1/market-intelligence/regime")
    assert res_reg.status_code == 200

    # Anomalies
    res_an = await client.get("/api/v1/market-intelligence/anomalies")
    assert res_an.status_code == 200
