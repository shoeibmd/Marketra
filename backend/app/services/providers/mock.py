import math
import uuid
from datetime import UTC, datetime, timedelta

from app.schemas.market_data import (
    NormalizedFundamental,
    NormalizedInstrument,
    NormalizedNewsArticle,
    NormalizedOHLCV,
    NormalizedQuote,
)
from app.services.providers.base import (
    BaseMarketDataProvider,
    InstrumentNotFoundError,
)


class MockProvider(BaseMarketDataProvider):
    """Deterministic Mock Market Data Provider for local dev and testing."""

    def __init__(self) -> None:
        super().__init__(provider_name="MOCK", rate_limit_per_minute=1000)
        self._instruments: dict[str, NormalizedInstrument] = {}
        self._fundamentals: dict[uuid.UUID, NormalizedFundamental] = {}
        self._news: dict[str, list[NormalizedNewsArticle]] = {}
        self._seed_mock_data()

    def _seed_mock_data(self) -> None:
        default_defs = [
            ("AAPL", "NASDAQ", "Apple Inc.", "US0378331005", "EQUITY", 185.0),
            ("MSFT", "NASDAQ", "Microsoft Corp.", "US5949181045", "EQUITY", 410.0),
            ("GOOGL", "NASDAQ", "Alphabet Inc.", "US02079K3059", "EQUITY", 175.0),
            ("TSLA", "NASDAQ", "Tesla Inc.", "US88160R1014", "EQUITY", 220.0),
            ("SPY", "NYSE", "SPDR S&P 500 ETF", "US78462F1030", "ETF", 510.0),
            ("BTC-USD", "CRYPTO", "Bitcoin USD", "BTC-USD-ISIN", "CRYPTO", 64000.0),
            ("ETH-USD", "CRYPTO", "Ethereum USD", "ETH-USD-ISIN", "CRYPTO", 3400.0),
        ]

        now = datetime.now(UTC)

        for symbol, exchange, name, isin, itype, base_price in default_defs:
            inst_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"mock:{symbol}")
            inst = NormalizedInstrument(
                id=inst_id,
                symbol=symbol,
                exchange_code=exchange,
                name=name,
                isin=isin,
                currency="USD",
                instrument_type=itype,
                provider_symbol=f"MOCK:{symbol}",
            )
            self._instruments[symbol] = inst

            self._fundamentals[inst.id] = NormalizedFundamental(
                instrument_id=inst.id,
                market_cap=base_price * 15_000_000_000 if itype != "CRYPTO" else base_price * 19_000_000,
                pe_ratio=28.5 if itype == "EQUITY" else None,
                pb_ratio=8.2 if itype == "EQUITY" else None,
                dividend_yield=0.012 if itype in ("EQUITY", "ETF") else None,
                eps=base_price / 28.5 if itype == "EQUITY" else None,
                beta=1.1,
                high_52_week=base_price * 1.25,
                low_52_week=base_price * 0.75,
            )

            articles: list[NormalizedNewsArticle] = []
            for i in range(7):
                articles.append(
                    NormalizedNewsArticle(
                        id=uuid.uuid5(uuid.NAMESPACE_DNS, f"news:{symbol}:{i}"),
                        instrument_id=inst.id,
                        source_name="Financial Times" if i % 2 == 0 else "Bloomberg",
                        title=f"{symbol} quarterly performance analysis and market outlook #{i + 1}",
                        summary=f"Analysis covering {name} ({symbol}) market movement and investor sentiment.",
                        content=f"Detailed financial article body discussing key revenue drivers for {symbol}.",
                        url=f"https://terminal.org/news/{symbol.lower()}-{i + 1}",
                        published_at=now - timedelta(days=i, hours=i * 2),
                    )
                )
            self._news[symbol] = articles

    async def search_instruments(self, query: str) -> list[NormalizedInstrument]:
        query_upper = query.upper().strip()
        results: list[NormalizedInstrument] = []
        for inst in self._instruments.values():
            if query_upper in inst.symbol or query_upper in inst.name.upper():
                results.append(inst)
        return results

    async def get_instrument_by_symbol(self, symbol: str, exchange_code: str = "US") -> NormalizedInstrument | None:
        return self._instruments.get(symbol.upper().strip())

    async def get_realtime_quote(self, instrument: NormalizedInstrument) -> NormalizedQuote:
        if instrument.symbol not in self._instruments:
            raise InstrumentNotFoundError(f"Instrument {instrument.symbol} not found")

        now = datetime.now(UTC)
        base_price = 64000.0 if "BTC" in instrument.symbol else 3400.0 if "ETH" in instrument.symbol else 185.0
        jitter = math.sin(now.timestamp() / 10.0) * (base_price * 0.005)
        last_price = round(base_price + jitter, 2)
        spread = round(last_price * 0.0005, 2)

        return NormalizedQuote(
            timestamp=now,
            instrument_id=instrument.id,
            bid_price=round(last_price - spread / 2, 2),
            bid_size=100.0,
            ask_price=round(last_price + spread / 2, 2),
            ask_size=150.0,
            last_price=last_price,
            last_size=50.0,
        )

    async def get_historical_ohlcv(
        self,
        instrument: NormalizedInstrument,
        interval: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[NormalizedOHLCV]:
        if instrument.symbol not in self._instruments:
            raise InstrumentNotFoundError(f"Instrument {instrument.symbol} not found")

        base_price = 64000.0 if "BTC" in instrument.symbol else 3400.0 if "ETH" in instrument.symbol else 200.0

        step = timedelta(days=1) if interval == "1d" else timedelta(minutes=1)
        current = start_time
        candles: list[NormalizedOHLCV] = []

        step_idx = 0
        while current <= end_time:
            drift = math.sin(step_idx / 20.0) * (base_price * 0.02)
            noise = (math.cos(step_idx) * 0.005) * base_price
            open_p = round(base_price + drift + noise, 2)
            high_p = round(open_p * 1.01, 2)
            low_p = round(open_p * 0.99, 2)
            close_p = round(open_p + (math.sin(step_idx) * 0.5), 2)
            vol = round(10000.0 + (step_idx % 100) * 250, 2)

            candles.append(
                NormalizedOHLCV(
                    timestamp=current,
                    instrument_id=instrument.id,
                    interval=interval,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=vol,
                )
            )
            current += step
            step_idx += 1

        return candles

    async def get_fundamentals(self, instrument: NormalizedInstrument) -> NormalizedFundamental | None:
        return self._fundamentals.get(instrument.id)

    async def get_news(
        self, instrument: NormalizedInstrument | None = None, limit: int = 10
    ) -> list[NormalizedNewsArticle]:
        if instrument and instrument.symbol in self._news:
            return self._news[instrument.symbol][:limit]

        all_news: list[NormalizedNewsArticle] = []
        for news_list in self._news.values():
            all_news.extend(news_list)
        all_news.sort(key=lambda x: x.published_at, reverse=True)
        return all_news[:limit]
