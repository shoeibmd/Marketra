import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.auth.jwt_handler import create_access_token


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "test@marketra.com", "role": "user"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_search_instruments_known_symbols(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Search for RELIANCE
        res = await ac.get("/api/v1/instruments/search?q=RELIANCE", headers=auth_headers)
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 1
        assert any(item["symbol"] == "RELIANCE" for item in items)

        # Search for TCS
        res_tcs = await ac.get("/api/v1/instruments/search?q=TCS", headers=auth_headers)
        assert res_tcs.status_code == 200
        items_tcs = res_tcs.json()
        assert len(items_tcs) >= 1
        assert any(item["symbol"] == "TCS" for item in items_tcs)

        # Search for INFY
        res_infy = await ac.get("/api/v1/instruments/search?q=INFY", headers=auth_headers)
        assert res_infy.status_code == 200
        items_infy = res_infy.json()
        assert len(items_infy) >= 1
        assert any(item["symbol"] == "INFY" for item in items_infy)


@pytest.mark.asyncio
async def test_search_instruments_non_existent(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/instruments/search?q=JAIN RESOURCE", headers=auth_headers)
        assert res.status_code == 200
        items = res.json()
        assert items == []


@pytest.mark.asyncio
async def test_historical_ohlcv_timeframes(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for timeframe in ["1m", "5m", "1h", "1d"]:
            res = await ac.get(f"/api/v1/market/ohlcv/RELIANCE?interval={timeframe}&days_back=30", headers=auth_headers)
            assert res.status_code == 200
            candles = res.json()
            assert len(candles) > 0
            for candle in candles:
                assert candle["high"] >= max(candle["open"], candle["close"])
                assert candle["low"] <= min(candle["open"], candle["close"])
                assert candle["volume"] >= 0


@pytest.mark.asyncio
async def test_market_overview_and_watchlist(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_overview = await ac.get("/api/v1/market/overview", headers=auth_headers)
        assert res_overview.status_code == 200
        data = res_overview.json()
        assert "indices" in data
        assert len(data["indices"]) >= 3

        res_watchlist = await ac.get("/api/v1/market/watchlist", headers=auth_headers)
        assert res_watchlist.status_code == 200
        items = res_watchlist.json()
        assert len(items) >= 3
