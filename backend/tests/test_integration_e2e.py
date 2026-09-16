from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import get_postgres_db
from app.main import app
from app.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_e2e_full_terminal_flow(async_session: AsyncSession) -> None:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_postgres_db] = _override_get_db
    client = TestClient(app)

    # 1. Register User
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "e2e_trader@terminal.org",
            "password": "SecurePassword123",
            "full_name": "E2E Alpha Trader",
        },
    )
    assert reg_res.status_code == 200

    # 2. Login User
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "e2e_trader@terminal.org",
            "password": "SecurePassword123",
        },
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 3. Search Instrument
    search_res = client.get("/api/v1/instruments/search?q=AAPL", headers=auth_headers)
    assert search_res.status_code == 200

    # 4. Fetch OHLCV Chart
    ohlcv_res = client.get("/api/v1/market/ohlcv/AAPL?interval=1d&days_back=5", headers=auth_headers)
    assert ohlcv_res.status_code == 200

    # 5. Create Custom Workspace
    ws_res = client.post(
        "/api/v1/workspaces",
        json={
            "name": "E2E Macro Workspace",
            "description": "Integration Test Workspace",
            "layout_config": [{"panelId": "p1", "panelType": "chart", "symbol": "AAPL"}],
        },
        headers=auth_headers,
    )
    assert ws_res.status_code == 200
    ws_id = ws_res.json()["id"]

    # 6. Execute RAG Query
    ai_res = client.post(
        "/api/v1/ai/query",
        json={"query": "Analyze Apple Inc. Q3 growth drivers"},
    )
    assert ai_res.status_code == 200

    # 7. Check Observability Health Detail
    health_res = client.get("/api/v1/healthz/detailed")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # 8. Clean up Workspace
    del_res = client.delete(f"/api/v1/workspaces/{ws_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # 9. Logout
    out_res = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert out_res.status_code == 200

    app.dependency_overrides.clear()
