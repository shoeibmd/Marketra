import uuid
from collections.abc import AsyncGenerator
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth.jwt_handler import create_access_token
from app.db.session import get_postgres_db
from app.main import app
from app.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_workspace_crud_and_isolation(async_session: AsyncSession) -> None:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_postgres_db] = _override_get_db
    client = TestClient(app)

    token = create_access_token({
        "sub": "trader@terminal.org",
        "user_id": "11111111-1111-1111-1111-111111111111",
        "role": "USER",
    })
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List user workspaces (auto-creates default)
    res_list = client.get("/api/v1/workspaces", headers=headers)
    assert res_list.status_code == 200
    workspaces = res_list.json()
    assert len(workspaces) == 1
    def_ws_id = workspaces[0]["id"]

    # 2. Get single workspace
    res_single = client.get(f"/api/v1/workspaces/{def_ws_id}", headers=headers)
    assert res_single.status_code == 200
    assert res_single.json()["name"] == "Indian Market Overview"

    # 3. Create new workspace
    new_ws_payload = {
        "name": "Crypto Analysis",
        "description": "Bitcoin & Altcoin focus",
        "is_default": False,
        "layout_config": [
            {"panelId": "p1", "panelType": "chart", "symbol": "BTC-USD", "x": 0, "y": 0, "w": 6, "h": 3}
        ],
    }
    res_create = client.post("/api/v1/workspaces", json=new_ws_payload, headers=headers)
    assert res_create.status_code == 200
    created_id = res_create.json()["id"]

    # 4. Update workspace layout
    update_payload = {
        "name": "Crypto & Macro Analysis",
        "layout_config": [
            {"panelId": "p1", "panelType": "chart", "symbol": "BTC-USD", "x": 0, "y": 0, "w": 12, "h": 4}
        ],
    }
    res_update = client.put(f"/api/v1/workspaces/{created_id}", json=update_payload, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Crypto & Macro Analysis"

    # 5. Verify ownership isolation - requesting non-existent returns 404
    fake_id = str(uuid.uuid4())
    res_invalid = client.get(f"/api/v1/workspaces/{fake_id}", headers=headers)
    assert res_invalid.status_code == 404

    # 6. Delete workspace
    res_delete = client.delete(f"/api/v1/workspaces/{created_id}", headers=headers)
    assert res_delete.status_code == 200
    assert res_delete.json()["status"] == "deleted"

    app.dependency_overrides.clear()
