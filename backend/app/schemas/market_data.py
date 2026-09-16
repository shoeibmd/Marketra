import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class NormalizedInstrument(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    symbol: str
    exchange_code: str
    name: str
    isin: str | None = None
    currency: str = "USD"
    instrument_type: str
    provider_symbol: str


class NormalizedQuote(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    instrument_id: uuid.UUID
    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float
    last_price: float
    last_size: float


class NormalizedOHLCV(BaseModel):
    timestamp: datetime
    instrument_id: uuid.UUID
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class NormalizedFundamental(BaseModel):
    instrument_id: uuid.UUID
    market_cap: float | None = None
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    dividend_yield: float | None = None
    eps: float | None = None
    beta: float | None = None
    high_52_week: float | None = None
    low_52_week: float | None = None


class NormalizedNewsArticle(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    instrument_id: uuid.UUID | None = None
    source_name: str
    title: str
    summary: str | None = None
    content: str | None = None
    url: str
    published_at: datetime
