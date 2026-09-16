from abc import ABC, abstractmethod
from datetime import datetime

from app.schemas.market_data import (
    NormalizedFundamental,
    NormalizedInstrument,
    NormalizedNewsArticle,
    NormalizedOHLCV,
    NormalizedQuote,
)


class BaseMarketDataProvider(ABC):
    """Abstract Base Class for all Market Data Providers.

    Rule: Core business logic and UI must ONLY consume normalized models.
    """

    def __init__(self, provider_name: str, rate_limit_per_minute: int = 60) -> None:
        self.provider_name = provider_name
        self.rate_limit_per_minute = rate_limit_per_minute

    @abstractmethod
    async def search_instruments(self, query: str) -> list[NormalizedInstrument]:
        """Search for instruments by symbol or name."""
        pass

    @abstractmethod
    async def get_instrument_by_symbol(self, symbol: str, exchange_code: str = "US") -> NormalizedInstrument | None:
        """Fetch a single normalized instrument."""
        pass

    @abstractmethod
    async def get_realtime_quote(self, instrument: NormalizedInstrument) -> NormalizedQuote:
        """Fetch latest quote for an instrument."""
        pass

    @abstractmethod
    async def get_historical_ohlcv(
        self,
        instrument: NormalizedInstrument,
        interval: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[NormalizedOHLCV]:
        """Fetch historical OHLCV data."""
        pass

    @abstractmethod
    async def get_fundamentals(self, instrument: NormalizedInstrument) -> NormalizedFundamental | None:
        """Fetch fundamentals data for an instrument."""
        pass

    @abstractmethod
    async def get_news(
        self, instrument: NormalizedInstrument | None = None, limit: int = 10
    ) -> list[NormalizedNewsArticle]:
        """Fetch latest news articles."""
        pass


class ProviderRateLimitError(Exception):
    """Exception raised when provider rate limit is exceeded."""

    pass


class InstrumentNotFoundError(Exception):
    """Exception raised when requested instrument is not supported."""

    pass
