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


def test_ai_query_endpoint() -> None:
    client = TestClient(app)
    res = client.post("/api/v1/ai/query", json={"query": "Analyze AAPL Q3 revenue growth"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert data["confidence"] > 0.8
    assert len(data["citations"]) >= 1
    assert "source_facts" in data
    assert "interpretation" in data


def test_ai_summarize_company_and_news() -> None:
    client = TestClient(app)
    res_comp = client.post("/api/v1/ai/summarize/company/AAPL")
    assert res_comp.status_code == 200
    assert "answer" in res_comp.json()

    res_news = client.post("/api/v1/ai/summarize/news?symbol=AAPL")
    assert res_news.status_code == 200
    assert "answer" in res_news.json()


@pytest.mark.asyncio
async def test_ai_document_upload_indexing(async_session: AsyncSession) -> None:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_postgres_db] = _override_get_db
    client = TestClient(app)

    doc_payload = {
        "title": "Apple Q3 10-Q Filing",
        "document_type": "10-Q",
        "content": (
            "Apple Inc. today announced financial results for its fiscal 2024 third quarter ended June 29, 2024. "
            "The Company posted quarterly revenue of $85.8 billion."
        ),
    }
    res = client.post("/api/v1/ai/documents", json=doc_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "indexed"
    assert res.json()["chunks_created"] >= 1

    app.dependency_overrides.clear()
