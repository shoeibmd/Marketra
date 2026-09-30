import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NormalizedNewsItem(BaseModel):
    """Normalized Data Model for Live News Intelligence."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    summary: str | None = None
    content: str | None = None
    source_name: str
    source_url: str | None = None
    original_url: str
    published_at: datetime
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    company: str | None = None
    symbol: str | None = None
    exchange: str | None = None
    category: str = "general"

    raw_metadata: dict[str, Any] = Field(default_factory=dict)
    content_hash: str | None = None
    processing_status: str = "normalized"


class BaseNewsProvider(ABC):
    """Abstract Base Class for News Providers."""

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    @abstractmethod
    async def fetch_news(self) -> list[NormalizedNewsItem]:
        """Fetch and return normalized news items from provider source."""
        pass
