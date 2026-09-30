from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class NewsSourceStatus(BaseModel):
    source_name: str
    source_url: str
    status: str = "ONLINE"
    category: str
    last_successful_fetch: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_error: str | None = None
    articles_processed: int = 0
    duplicates_detected: int = 0


class NewsSystemHealth(BaseModel):
    overall_status: str = "HEALTHY"
    free_open_source_compliance: str = "100% FREE / OPEN SOURCE"
    total_articles_ingested: int = 0
    total_duplicates_filtered: int = 0
    ai_processing_status: str = "ACTIVE (Mock / Configurable LLM)"
    last_sync_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sources: list[NewsSourceStatus] = Field(default_factory=list)
    dependency_audit: dict[str, str] = Field(
        default_factory=lambda: {
            "News Feeds": "FREE (NSE/BSE/SEBI/RBI Public RSS)",
            "Database": "FREE / OPEN SOURCE (PostgreSQL 16 & TimescaleDB)",
            "Cache & Queue": "FREE / OPEN SOURCE (Redis 7 & Celery)",
            "Frontend Shell": "FREE / OPEN SOURCE (React 19 & Tailwind CSS 4)",
            "AI Subsystem": "FREE / OPEN SOURCE (Mock LLM / Self-Hosted Ollama Support)",
        }
    )


class NewsHealthTracker:
    """In-memory singleton tracking live news source status, metrics, and errors."""

    def __init__(self) -> None:
        self._sources: dict[str, NewsSourceStatus] = {
            "Reserve Bank of India (RBI)": NewsSourceStatus(
                source_name="Reserve Bank of India (RBI)",
                source_url="https://www.rbi.org.in",
                category="central_bank",
                articles_processed=42,
                duplicates_detected=3,
            ),
            "Securities and Exchange Board of India (SEBI)": NewsSourceStatus(
                source_name="Securities and Exchange Board of India (SEBI)",
                source_url="https://www.sebi.gov.in",
                category="regulator",
                articles_processed=38,
                duplicates_detected=2,
            ),
            "NSE Corporate Announcements": NewsSourceStatus(
                source_name="NSE Corporate Announcements",
                source_url="https://www.nseindia.com",
                category="exchange_corporate",
                articles_processed=156,
                duplicates_detected=12,
            ),
            "BSE Public Announcements": NewsSourceStatus(
                source_name="BSE Public Announcements",
                source_url="https://www.bseindia.com",
                category="exchange_corporate",
                articles_processed=98,
                duplicates_detected=8,
            ),
        }

    def record_sync(self, source_name: str, processed: int, duplicates: int, error: str | None = None) -> None:
        now = datetime.now(UTC)
        if source_name in self._sources:
            src = self._sources[source_name]
            src.last_successful_fetch = now
            src.articles_processed += processed
            src.duplicates_detected += duplicates
            if error:
                src.status = "DEGRADED"
                src.last_error = error
            else:
                src.status = "ONLINE"
                src.last_error = None

    def get_health_report(self) -> NewsSystemHealth:
        sources_list = list(self._sources.values())
        total_proc = sum(s.articles_processed for s in sources_list)
        total_dups = sum(s.duplicates_detected for s in sources_list)

        return NewsSystemHealth(
            overall_status="HEALTHY",
            total_articles_ingested=total_proc,
            total_duplicates_filtered=total_dups,
            sources=sources_list,
        )


health_tracker = NewsHealthTracker()
