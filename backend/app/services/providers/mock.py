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

INDIAN_STOCKS = [
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd.", "exchange": "NSE", "base_price": 2850.0},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "exchange": "NSE", "base_price": 3920.0},
    {"symbol": "INFY", "name": "Infosys Ltd.", "exchange": "NSE", "base_price": 1610.0},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd.", "exchange": "NSE", "base_price": 1650.0},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd.", "exchange": "NSE", "base_price": 1180.0},
    {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE", "base_price": 820.0},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd.", "exchange": "NSE", "base_price": 1420.0},
    {"symbol": "ITC", "name": "ITC Limited", "exchange": "NSE", "base_price": 490.0},
    {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "exchange": "NSE", "base_price": 1780.0},
    {"symbol": "LT", "name": "Larsen & Toubro Ltd.", "exchange": "NSE", "base_price": 3650.0},
    {"symbol": "AXISBANK", "name": "Axis Bank Ltd.", "exchange": "NSE", "base_price": 1160.0},
    {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd.", "exchange": "NSE", "base_price": 3250.0},
    {"symbol": "MARUTI", "name": "Maruti Suzuki India", "exchange": "NSE", "base_price": 12400.0},
    {"symbol": "TITAN", "name": "Titan Company Ltd.", "exchange": "NSE", "base_price": 3450.0},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd.", "exchange": "NSE", "base_price": 6850.0},
]

INDIAN_INDICES = [
    {"symbol": "NIFTY50", "name": "Nifty 50 Index", "exchange": "NSE", "base_price": 24800.0},
    {"symbol": "BANKNIFTY", "name": "Nifty Bank Index", "exchange": "NSE", "base_price": 51200.0},
    {"symbol": "SENSEX", "name": "BSE Sensex Index", "exchange": "BSE", "base_price": 81500.0},
]


class MockProvider(BaseMarketDataProvider):
    """Deterministic Mock Market Data Provider for Indian Stocks (NSE/BSE)."""

    def __init__(self) -> None:
        super().__init__(provider_name="MOCK", rate_limit_per_minute=1000)
        self._instruments: dict[str, NormalizedInstrument] = {}
        self._fundamentals: dict[uuid.UUID, NormalizedFundamental] = {}
        self._news: dict[str, list[NormalizedNewsArticle]] = {}
        self._seed_mock_data()

    def _seed_mock_data(self) -> None:
        now = datetime.now(UTC)

        all_defs = []
        for stock in INDIAN_STOCKS:
            all_defs.append(
                (
                    stock["symbol"],
                    stock["exchange"],
                    stock["name"],
                    f"INE{stock['symbol']}ISIN",
                    "EQUITY",
                    stock["base_price"],
                )
            )
        for idx in INDIAN_INDICES:
            all_defs.append(
                (
                    idx["symbol"],
                    idx["exchange"],
                    idx["name"],
                    f"INDEX{idx['symbol']}ISIN",
                    "INDEX",
                    idx["base_price"],
                )
            )

        for symbol, exchange, name, isin, itype, base_price in all_defs:
            inst_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"mock:{symbol}")
            inst = NormalizedInstrument(
                id=inst_id,
                symbol=symbol,
                exchange_code=exchange,
                name=name,
                isin=isin,
                currency="INR",
                instrument_type=itype,
                provider_symbol=f"MOCK:{symbol}",
            )
            self._instruments[symbol] = inst

            self._fundamentals[inst.id] = NormalizedFundamental(
                instrument_id=inst.id,
                market_cap=base_price * 100_000_000 if itype != "INDEX" else None,
                pe_ratio=24.5 if itype == "EQUITY" else None,
                pb_ratio=3.8 if itype == "EQUITY" else None,
                dividend_yield=0.015 if itype == "EQUITY" else None,
                eps=base_price / 24.5 if itype == "EQUITY" else None,
                beta=1.05,
                high_52_week=base_price * 1.2,
                low_52_week=base_price * 0.8,
            )

            articles: list[NormalizedNewsArticle] = []
            for i in range(7):
                articles.append(
                    NormalizedNewsArticle(
                        id=uuid.uuid5(uuid.NAMESPACE_DNS, f"news:{symbol}:{i}"),
                        instrument_id=inst.id,
                        source_name="Economic Times" if i % 2 == 0 else "Moneycontrol",
                        title=f"{symbol} quarterly earnings performance and Indian market outlook #{i + 1}",
                        summary=f"Market analysis covering {name} ({symbol}) on NSE/BSE and sector trends.",
                        content=f"Detailed financial analysis on revenue growth and margin trajectory for {symbol}.",
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

    async def get_instrument_by_symbol(self, symbol: str, exchange_code: str = "NSE") -> NormalizedInstrument | None:
        return self._instruments.get(symbol.upper().strip())

    async def get_realtime_quote(self, instrument: NormalizedInstrument) -> NormalizedQuote:
        if instrument.symbol not in self._instruments:
            raise InstrumentNotFoundError(f"Instrument {instrument.symbol} not found")

        now = datetime.now(UTC)
        base_price = 2850.0
        for stock in INDIAN_STOCKS + INDIAN_INDICES:
            if stock["symbol"] == instrument.symbol:
                base_price = stock["base_price"]
                break

        jitter = math.sin(now.timestamp() / 10.0) * (base_price * 0.003)
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

        base_price = 2850.0
        for stock in INDIAN_STOCKS + INDIAN_INDICES:
            if stock["symbol"] == instrument.symbol:
                base_price = stock["base_price"]
                break

        step = timedelta(days=1) if interval == "1d" else timedelta(minutes=1)
        current = start_time
        candles: list[NormalizedOHLCV] = []

        step_idx = 0
        while current <= end_time:
            drift = math.sin(step_idx / 20.0) * (base_price * 0.015)
            noise = (math.cos(step_idx) * 0.004) * base_price
            open_p = round(base_price + drift + noise, 2)
            high_p = round(open_p * 1.008, 2)
            low_p = round(open_p * 0.992, 2)
            close_p = round(open_p + (math.sin(step_idx) * 0.5), 2)
            vol = round(25000.0 + (step_idx % 100) * 500, 2)

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
