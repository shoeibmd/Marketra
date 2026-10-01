import uuid
from datetime import datetime, timezone, timedelta
import zoneinfo
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.domain import FinancialEvent, Instrument, EventMarketObservation, OHLCV
from app.services.analytics.event_market_analytics import (
    EventMarketAnalyticsService,
    classify_trading_session,
    IST,
)


def test_classify_trading_session() -> None:
    # 1. Pre-market: Monday 08:30 IST (03:00 UTC)
    dt_pre = datetime(2026, 3, 30, 3, 0, tzinfo=timezone.utc)
    assert classify_trading_session(dt_pre) == "PRE_MARKET"

    # 2. Intraday: Monday 11:30 IST (06:00 UTC)
    dt_intra = datetime(2026, 3, 30, 6, 0, tzinfo=timezone.utc)
    assert classify_trading_session(dt_intra) == "INTRADAY"

    # 3. Post-market: Monday 17:00 IST (11:30 UTC)
    dt_post = datetime(2026, 3, 30, 11, 30, tzinfo=timezone.utc)
    assert classify_trading_session(dt_post) == "POST_MARKET"

    # 4. Weekend: Sunday
    dt_weekend = datetime(2026, 3, 29, 6, 0, tzinfo=timezone.utc)
    assert classify_trading_session(dt_weekend) == "WEEKEND"

    # 5. Market Holiday: Republic Day 2026-01-26
    dt_holiday = datetime(2026, 1, 26, 6, 0, tzinfo=timezone.utc)
    assert classify_trading_session(dt_holiday) == "MARKET_HOLIDAY"


def test_aggregate_statistics_sample_size_threshold() -> None:
    # n < 5 threshold test
    obs_small = [
        EventMarketObservation(return_1d_pct=1.5),
        EventMarketObservation(return_1d_pct=-0.5),
        EventMarketObservation(return_1d_pct=2.0),
    ]
    stats_small = EventMarketAnalyticsService.compute_aggregate_statistics(obs_small, "1d")
    assert stats_small["insufficient_sample"] is True
    assert stats_small["sample_size"] == 3
    assert "Insufficient historical sample" in stats_small["message"]

    # n >= 5 valid test
    obs_large = [
        EventMarketObservation(return_1d_pct=1.0),
        EventMarketObservation(return_1d_pct=2.0),
        EventMarketObservation(return_1d_pct=-1.0),
        EventMarketObservation(return_1d_pct=3.0),
        EventMarketObservation(return_1d_pct=0.5),
    ]
    stats_large = EventMarketAnalyticsService.compute_aggregate_statistics(obs_large, "1d")
    assert stats_large["insufficient_sample"] is False
    assert stats_large["sample_size"] == 5
    assert stats_large["mean_return_pct"] == 1.1


@pytest.mark.asyncio
async def test_analytics_api_endpoints() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Event Market Context 404 test for non-existent event
        random_id = str(uuid.uuid4())
        res_ctx = await ac.get(f"/api/v1/events/{random_id}/market-context")
        assert res_ctx.status_code == 404

        # Event type analytics test
        res_types = await ac.get("/api/v1/analytics/event-types?event_type=ACQUISITION")
        assert res_types.status_code == 200
        data_types = res_types.json()
        assert data_types["event_type"] == "ACQUISITION"
        assert "aggregate_statistics_1d" in data_types
