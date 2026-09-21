import asyncio
import logging
from datetime import UTC, datetime, timedelta

from app.services.ingestion import IngestionPipeline

from app.db.session import PostgresSessionLocal
from app.services.providers.mock import MockProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_mock_data")


async def seed_database() -> None:
    """Seed relational database and TimescaleDB with Indian market instruments and historical data."""
    mock_provider = MockProvider()
    async with PostgresSessionLocal() as session:
        logger.info("Seeding Indian Market Instruments...")
        instruments = await mock_provider.search_instruments("")

        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=30)

        for inst in instruments:
            logger.info(f"Seeding instrument {inst.symbol} ({inst.exchange_code})")
            await IngestionPipeline.upsert_instrument(session, inst)

            fund = await mock_provider.get_fundamentals(inst)
            if fund:
                await IngestionPipeline.ingest_fundamentals(session, fund)

            candles = await mock_provider.get_historical_ohlcv(
                inst, interval="1d", start_time=start_time, end_time=end_time
            )
            count = await IngestionPipeline.bulk_ingest_ohlcv(session, candles)
            logger.info(f"Ingested {count} candles for {inst.symbol}")

            news = await mock_provider.get_news(inst, limit=5)
            await IngestionPipeline.bulk_ingest_news(session, news)

        logger.info("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
