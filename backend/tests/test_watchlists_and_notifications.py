import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.auth.jwt_handler import create_access_token
from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import User, Watchlist, AlertPreference


class MockAsyncSession:
    """Mock async session for endpoint unit testing."""

    def __init__(self) -> None:
        self.added: list[object] = []
        self.deleted: list[object] = []
        self.watchlists: list[Watchlist] = []
        self.preferences: list[AlertPreference] = []

    def add(self, instance: object) -> None:
        self.added.append(instance)
        if isinstance(instance, Watchlist):
            self.watchlists.append(instance)
        elif isinstance(instance, AlertPreference):
            self.preferences.append(instance)

    async def commit(self) -> None:
        pass

    async def refresh(self, instance: object) -> None:
        pass

    async def execute(self, stmt: object) -> "MockResult":
        return MockResult(self)

    async def delete(self, instance: object) -> None:
        self.deleted.append(instance)


class MockResult:

    def __init__(self, session: MockAsyncSession) -> None:
        self.session = session

    def scalars(self) -> "MockResult":
        return self

    def all(self) -> list[object]:
        return self.session.watchlists

    def scalar_one_or_none(self) -> object | None:
        return self.session.preferences[0] if self.session.preferences else None

    def scalar(self) -> int:
        return 0


@pytest.mark.asyncio
async def test_watchlist_and_notifications_flow() -> None:
    u1 = User(id=uuid.uuid4(), email="user1@terminal.local", hashed_password="hash1", full_name="User One")
    u2 = User(id=uuid.uuid4(), email="user2@terminal.local", hashed_password="hash2", full_name="User Two")

    token1 = create_access_token({"sub": u1.email})
    headers1 = {"Authorization": f"Bearer {token1}"}

    mock_db = MockAsyncSession()

    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return u1

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. List watchlists
            res1 = await ac.get("/api/v1/watchlists", headers=headers1)
            assert res1.status_code == 200
            wls1 = res1.json()
            assert len(wls1) >= 1
            assert wls1[0]["name"] == "My Watchlist"

            # 2. Create custom watchlist
            res_create = await ac.post("/api/v1/watchlists", json={"name": "Tech Giants"}, headers=headers1)
            assert res_create.status_code == 201
            assert res_create.json()["name"] == "Tech Giants"

            # 3. Check preferences
            res_pref = await ac.get("/api/v1/watchlists/preferences/me", headers=headers1)
            assert res_pref.status_code == 200

            # 4. Check notifications
            res_notif = await ac.get("/api/v1/notifications", headers=headers1)
            assert res_notif.status_code == 200

            # 5. Unread count
            res_count = await ac.get("/api/v1/notifications/unread-count", headers=headers1)
            assert res_count.status_code == 200
            assert "unread_count" in res_count.json()
    finally:
        app.dependency_overrides.clear()
