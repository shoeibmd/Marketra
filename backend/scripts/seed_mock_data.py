import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.password import hash_password
from app.db.session import PostgresSessionLocal
from app.models.domain import Exchange, Fundamental, Instrument, NewsArticle, OHLCV, Quote, User, Workspace
from app.services.providers.mock import INDIAN_INDICES, INDIAN_STOCKS, MockProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_mock_data")


async def seed_database() -> None:
    """Seed relational database with default admin user, Indian exchanges, instruments, fundamentals, news, and quotes/OHLCV data."""
    mock_provider = MockProvider()

    async with PostgresSessionLocal() as session:
        logger.info("1. Seeding default Admin User (admin@marketra.com)...")
        user_stmt = select(User).where(User.email == "admin@marketra.com")
        res_user = await session.execute(user_stmt)
        user = res_user.scalar_one_or_none()

        if not user:
            user = User(
                id=uuid.uuid4(),
                email="admin@marketra.com",
                hashed_password=hash_password("Password123!"),
                full_name="Admin User",
                role="admin",
                is_active=True,
                is_superuser=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info("Admin user created successfully.")
        else:
            logger.info("Admin user already exists.")

        logger.info("2. Seeding default Indian Market Workspace...")
        ws_stmt = select(Workspace).where(Workspace.user_id == user.id, Workspace.is_default == True)  # noqa: E712
        res_ws = await session.execute(ws_stmt)
        default_ws = res_ws.scalar_one_or_none()

        if not default_ws:
            default_layout = [
                {
                    "panelId": "panel_chart_1",
                    "panelType": "chart",
                    "title": "RELIANCE Technical Candlestick Chart",
                    "symbol": "RELIANCE",
                    "x": 0,
                    "y": 0,
                    "w": 8,
                    "h": 3,
                },
                {
                    "panelId": "panel_overview_1",
                    "panelType": "overview",
                    "title": "NIFTY50 & BSE Sensex Overview",
                    "symbol": "NIFTY50",
                    "x": 8,
                    "y": 0,
                    "w": 4,
                    "h": 3,
                },
            ]
            default_ws = Workspace(
                id=uuid.uuid4(),
                user_id=user.id,
                name="Indian Market Overview",
                description="Default workspace pre-seeded with Indian NSE/BSE market panels.",
                is_default=True,
                layout_config=default_layout,
            )
            session.add(default_ws)
            await session.commit()
            logger.info("Default Indian Market workspace created.")

        logger.info("3. Seeding Indian Market Exchanges (NSE, BSE)...")
        exchanges = [
            {"code": "NSE", "name": "National Stock Exchange of India", "country": "India", "timezone": "Asia/Kolkata"},
            {"code": "BSE", "name": "BSE Limited (Bombay Stock Exchange)", "country": "India", "timezone": "Asia/Kolkata"},
        ]
        exchange_map: dict[str, uuid.UUID] = {}

        for ex in exchanges:
            ex_stmt = select(Exchange).where(Exchange.code == ex["code"])
            res_ex = await session.execute(ex_stmt)
            existing_ex = res_ex.scalar_one_or_none()

            if not existing_ex:
                new_ex = Exchange(
                    id=uuid.uuid4(),
                    code=ex["code"],
                    name=ex["name"],
                    country=ex["country"],
                    timezone=ex["timezone"],
                )
                session.add(new_ex)
                await session.commit()
                await session.refresh(new_ex)
                exchange_map[ex["code"]] = new_ex.id
                logger.info(f"Exchange {ex['code']} created.")
            else:
                exchange_map[ex["code"]] = existing_ex.id

        logger.info("4. Seeding Indian Instruments & Fundamentals...")
        now = datetime.now(UTC)
        start_time = now - timedelta(days=30)

        for stock in INDIAN_STOCKS + INDIAN_INDICES:
            symbol = stock["symbol"]
            ex_code = stock["exchange"]
            ex_id = exchange_map.get(ex_code)

            inst_stmt = select(Instrument).where(
                Instrument.symbol == symbol, Instrument.exchange_code == ex_code
            )
            res_inst = await session.execute(inst_stmt)
            inst = res_inst.scalar_one_or_none()

            if not inst:
                inst_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"mock:{symbol}")
                inst = Instrument(
                    id=inst_id,
                    exchange_id=ex_id,
                    symbol=symbol,
                    exchange_code=ex_code,
                    name=stock["name"],
                    isin=f"INE{symbol}ISIN",
                    currency="INR",
                    instrument_type="EQUITY" if "INDEX" not in symbol else "INDEX",
                    is_active=True,
                )
                session.add(inst)
                await session.commit()
                await session.refresh(inst)
                logger.info(f"Instrument {symbol} ({ex_code}) seeded.")

            fund_stmt = select(Fundamental).where(Fundamental.instrument_id == inst.id)
            res_fund = await session.execute(fund_stmt)
            fund = res_fund.scalar_one_or_none()

            if not fund:
                base_p = stock["base_price"]
                is_equity = inst.instrument_type == "EQUITY"
                fund = Fundamental(
                    id=uuid.uuid4(),
                    instrument_id=inst.id,
                    market_cap=base_p * 100_000_000 if is_equity else None,
                    pe_ratio=24.5 if is_equity else None,
                    pb_ratio=3.8 if is_equity else None,
                    dividend_yield=0.015 if is_equity else None,
                    eps=base_p / 24.5 if is_equity else None,
                    beta=1.05,
                    high_52_week=base_p * 1.2,
                    low_52_week=base_p * 0.8,
                )
                session.add(fund)
                await session.commit()

            # Seed Realtime Quote
            norm_inst = await mock_provider.get_instrument_by_symbol(symbol)
            if norm_inst:
                q = await mock_provider.get_realtime_quote(norm_inst)
                quote_entry = Quote(
                    timestamp=q.timestamp,
                    instrument_id=inst.id,
                    bid_price=q.bid_price,
                    bid_size=q.bid_size,
                    ask_price=q.ask_price,
                    ask_size=q.ask_size,
                    last_price=q.last_price,
                    last_size=q.last_size,
                )
                session.add(quote_entry)

                # Seed 30 days OHLCV Candles
                candles = await mock_provider.get_historical_ohlcv(
                    norm_inst, interval="1d", start_time=start_time, end_time=now
                )
                for c in candles:
                    ohlcv_entry = OHLCV(
                        timestamp=c.timestamp,
                        instrument_id=inst.id,
                        interval=c.interval,
                        open=c.open,
                        high=c.high,
                        low=c.low,
                        close=c.close,
                        volume=c.volume,
                    )
                    session.add(ohlcv_entry)

                # Seed News Articles
                news_list = await mock_provider.get_news(norm_inst, limit=5)
                for n in news_list:
                    article = NewsArticle(
                        id=n.id,
                        instrument_id=inst.id,
                        title=n.title,
                        summary=n.summary,
                        content=n.content,
                        url=n.url,
                        published_at=n.published_at,
                    )
                    session.add(article)

                await session.commit()

        logger.info("Database seeding successfully completed!")


if __name__ == "__main__":
    asyncio.run(seed_database())
