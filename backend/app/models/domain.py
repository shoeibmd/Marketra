import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    layout_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("exchanges.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    exchange_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    isin: Mapped[str | None] = mapped_column(String(12), unique=True, index=True, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    instrument_type: Mapped[str] = mapped_column(String(30), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (Index("ix_instruments_symbol_exchange", "symbol", "exchange_code", unique=True),)


class ProviderSymbol(Base):
    __tablename__ = "provider_symbols"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index(
            "ix_provider_symbols_provider_symbol",
            "provider_name",
            "provider_symbol",
            unique=True,
        ),
    )


class Quote(Base):
    __tablename__ = "quotes"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    instrument_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, nullable=False)
    bid_price: Mapped[float] = mapped_column(Float, nullable=False)
    bid_size: Mapped[float] = mapped_column(Float, nullable=False)
    ask_price: Mapped[float] = mapped_column(Float, nullable=False)
    ask_size: Mapped[float] = mapped_column(Float, nullable=False)
    last_price: Mapped[float] = mapped_column(Float, nullable=False)
    last_size: Mapped[float] = mapped_column(Float, nullable=False)


class OHLCV(Base):
    __tablename__ = "ohlcv"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    instrument_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, nullable=False)
    interval: Mapped[str] = mapped_column(String(10), primary_key=True, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)


class Fundamental(Base):
    __tablename__ = "fundamentals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    pe_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    pb_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    dividend_yield: Mapped[float | None] = mapped_column(Float, nullable=True)
    eps: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta: Mapped[float | None] = mapped_column(Float, nullable=True)
    high_52_week: Mapped[float | None] = mapped_column(Float, nullable=True)
    low_52_week: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str] = mapped_column(String(100), default="Unknown Source", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Intelligence & Normalization Fields
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    symbol: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    exchange: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False, index=True)
    raw_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True, unique=True)
    processing_status: Mapped[str] = mapped_column(String(30), default="raw", nullable=False, index=True)

    # AI Intelligence Fields
    ai_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    ai_importance: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    ai_impact: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    ai_analysis_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class ArticleInstrument(Base):
    """Junction table supporting one news article affecting multiple instruments/companies."""

    __tablename__ = "article_instruments"

    article_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("news_articles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class FinancialEvent(Base):
    """Phase 10: Structured Financial Event model."""

    __tablename__ = "financial_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    news_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("news_articles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    cluster_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), default="OTHER", nullable=False, index=True)
    event_title: Mapped[str] = mapped_column(String(512), nullable=False)
    event_summary: Mapped[str] = mapped_column(Text, nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    primary_company_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    importance: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.90, nullable=False)

    source_name: Mapped[str] = mapped_column(String(100), default="Exchange Disclosure", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    verified_facts: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    ai_analysis_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    potential_impact: Mapped[str] = mapped_column(String(20), default="NEUTRAL", nullable=False)
    uncertainties: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class EventCompanyRelationship(Base):
    """Phase 10: Role classification mapping companies to financial events."""

    __tablename__ = "event_company_relationships"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("financial_events.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(30), default="PRIMARY_SUBJECT", nullable=False, index=True)
    relationship_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), default="My Watchlist", nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class WatchlistCompany(Base):
    __tablename__ = "watchlist_companies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    watchlist_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("watchlist_id", "instrument_id", name="uq_watchlist_instrument"),
    )


class AlertPreference(Base):
    __tablename__ = "alert_preferences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    minimum_importance: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    event_types_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    filter_setting: Mapped[str] = mapped_column(String(50), default="ALL_IMPORTANT_NEWS", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("financial_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(50), default="watchlist_alert", nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_notification"),
    )


class EventMarketObservation(Base):
    """Phase 13: Derived historical observations linking financial events to market data windows."""

    __tablename__ = "event_market_observations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("financial_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    session_classification: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # PRE_MARKET, INTRADAY, POST_MARKET, WEEKEND, MARKET_HOLIDAY

    baseline_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    baseline_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_at_event: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Historical return windows
    return_1d_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    return_3d_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    return_5d_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    return_10d_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    return_20d_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Volume changes
    volume_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_change_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    calculation_method: Mapped[str] = mapped_column(String(100), default="PREVIOUS_CLOSE_BASELINE", nullable=False)
    data_status: Mapped[str] = mapped_column(String(30), default="AVAILABLE", nullable=False, index=True)  # AVAILABLE, INSUFFICIENT
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("event_id", "instrument_id", name="uq_event_instrument_observation"),
    )


# Phase 14: Paper Trading & Strategy Simulation Models
class PaperTradingAccount(Base):
    __tablename__ = "paper_trading_accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), default="Primary Paper Account", nullable=False)
    initial_cash: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("1000000.00"), nullable=False)
    available_cash: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("1000000.00"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY, SELL
    order_type: Mapped[str] = mapped_column(String(20), default="MARKET", nullable=False)  # MARKET, LIMIT
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    requested_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    executed_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, EXECUTED, REJECTED, CANCELLED
    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PaperPosition(Base):
    __tablename__ = "paper_positions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    average_entry_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("account_id", "instrument_id", name="uq_account_instrument_position"),
    )


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    execution_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fees: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    slippage: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.00"), nullable=False)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class PaperPortfolioSnapshot(Base):
    __tablename__ = "paper_portfolio_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    cash: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    positions_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_equity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)


class BacktestJob(Base):
    __tablename__ = "backtest_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # SMA_CROSSOVER, EVENT_REACTION_RESEARCH
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("1000000.00"), nullable=False)
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED", nullable=False, index=True)  # QUEUED, RUNNING, COMPLETED, FAILED
    error_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("backtest_jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    final_equity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_return_pct: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    max_drawdown_pct: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    trade_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    win_rate_pct: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    equity_curve_json: Mapped[list[Any]] = mapped_column(JSON, default=list, nullable=False)
    trades_json: Mapped[list[Any]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# Phase 15: Broker Integration & Risk Engine Models
class BrokerAccount(Base):
    __tablename__ = "broker_accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_name: Mapped[str] = mapped_column(String(50), default="MOCK_LIVE_BROKER", nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="NOT_CONFIGURED", nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class BrokerOrderMapping(Base):
    __tablename__ = "broker_order_mappings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_order_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    broker_order_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    execution_mode: Mapped[str] = mapped_column(String(20), default="PAPER", nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    order_type: Mapped[str] = mapped_column(String(20), default="MARKET", nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    filled_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    requested_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    avg_executed_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="CREATED", nullable=False, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class RiskLimit(Base):
    __tablename__ = "risk_limits"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    max_order_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("10000"), nullable=False)
    max_order_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("250000.00"), nullable=False)
    max_portfolio_exposure_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("80.00"), nullable=False)
    daily_loss_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("50000.00"), nullable=False)
    max_open_orders: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class RiskDecision(Base):
    __tablename__ = "risk_decisions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_order_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(50), nullable=False)
    input_value: Mapped[str] = mapped_column(String(100), nullable=False)
    threshold_value: Mapped[str] = mapped_column(String(100), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class TradingAuditLog(Base):
    __tablename__ = "trading_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    execution_mode: Mapped[str] = mapped_column(String(20), default="PAPER", nullable=False)
    client_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class ReconciliationRecord(Base):
    __tablename__ = "reconciliation_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_order_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    broker_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    discrepancy_details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


# Phase 16: Controlled Live Trading & Activation Models
class LiveTradingActivationLog(Base):
    __tablename__ = "live_trading_activation_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(20), nullable=False)
    previous_state_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    new_state_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    source_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class OrderConfirmation(Base):
    __tablename__ = "order_confirmations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    confirmation_token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    client_order_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    order_params_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_invalidated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# Phase 24: Portfolio Intelligence Models
class PortfolioAnalyticsSnapshot(Base):
    __tablename__ = "portfolio_analytics_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    total_equity: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    positions_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    drawdown_pct: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    exposure_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# Phase 25: Portfolio Risk Analytics Models
class PortfolioRiskSnapshot(Base):
    __tablename__ = "portfolio_risk_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    portfolio_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    volatility_pct: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    var_95_pct: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    expected_shortfall_95_pct: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    drawdown_pct: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    sector_concentration_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    company_concentration_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    diversification_metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    risk_contribution_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    methodology_metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    data_quality_status: Mapped[str] = mapped_column(String(30), default="AVAILABLE", nullable=False, index=True)


# Phase 26: Portfolio Risk Monitoring & Alerts Models
class PortfolioRiskAlertPreference(Base):
    __tablename__ = "portfolio_risk_alert_preferences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    drawdown_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("5.00"), nullable=False)
    daily_loss_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("3.00"), nullable=False)
    daily_loss_threshold_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("50000.00"), nullable=False)
    var_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("5.00"), nullable=False)
    expected_shortfall_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("7.50"), nullable=False)
    company_concentration_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("25.00"), nullable=False)
    sector_concentration_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("40.00"), nullable=False)
    correlation_threshold: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.75"), nullable=False)
    volatility_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("20.00"), nullable=False)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    enabled_alerts_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default_utc_now, onupdate=utc_now, nullable=False
    )


class PortfolioRiskAlert(Base):
    __tablename__ = "portfolio_risk_alerts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="WARNING", nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    threshold_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="PCT", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="TRIGGERED", nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    data_quality_status: Mapped[str] = mapped_column(String(30), default="AVAILABLE", nullable=False)
    affected_symbols_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    affected_sectors_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    recovered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)


class PortfolioRiskAlertState(Base):
    __tablename__ = "portfolio_risk_alert_states"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(20), default="NORMAL", nullable=False)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    cooldown_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "fingerprint", name="uq_user_risk_alert_fingerprint"),
    )


class AIDocument(Base):
    __tablename__ = "ai_documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("instruments.id", ondelete="SET NULL"),
        nullable=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AIDocumentChunk(Base):
    __tablename__ = "ai_document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
