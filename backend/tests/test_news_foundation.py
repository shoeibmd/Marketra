import pytest
from app.services.news.deduplication import compute_content_hash
from app.services.news.rss import RSSNewsProvider
from app.services.tasks import sync_live_news_feeds


@pytest.mark.asyncio
async def test_rss_news_provider_fetch_and_normalization() -> None:
    provider = RSSNewsProvider()
    items = await provider.fetch_news()

    assert len(items) > 0
    for item in items:
        assert item.title is not None
        assert item.source_name is not None
        assert item.original_url is not None
        assert item.content_hash is not None
        assert item.processing_status == "normalized"


def test_content_hash_deduplication() -> None:
    hash1 = compute_content_hash(
        "Reliance Industries - Q3 Results",
        "2025-01-16T12:15:00Z",
        "Reliance Industries Ltd",
    )
    hash2 = compute_content_hash(
        "reliance industries   q3 results!!!",
        "2025-01-16T12:15:00Z",
        "reliance industries ltd",
    )
    assert hash1 == hash2

    hash3 = compute_content_hash(
        "Tata Consultancy Services - Board Outcome",
        "2025-01-15T14:00:00Z",
        "TCS",
    )
    assert hash1 != hash3
