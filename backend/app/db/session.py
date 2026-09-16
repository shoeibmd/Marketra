from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Relational Database Engine
postgres_engine = create_async_engine(
    settings.postgres_async_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

PostgresSessionLocal = async_sessionmaker(
    bind=postgres_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Time-Series Database Engine
timescale_engine = create_async_engine(
    settings.timescale_async_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

TimescaleSessionLocal = async_sessionmaker(
    bind=timescale_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_postgres_db() -> AsyncGenerator[AsyncSession, None]:
    async with PostgresSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_timescale_db() -> AsyncGenerator[AsyncSession, None]:
    async with TimescaleSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
