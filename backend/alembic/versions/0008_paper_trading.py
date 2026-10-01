"""paper trading and strategy simulation

Revision ID: 0008_paper_trading
Revises: 0007_event_market_observations
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0008_paper_trading"
down_revision: Union[str, None] = "0007_event_market_observations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. paper_trading_accounts
    op.create_table(
        "paper_trading_accounts",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=100), server_default="Primary Paper Account", nullable=False),
        sa.Column("initial_cash", sa.Numeric(precision=18, scale=2), server_default="1000000.00", nullable=False),
        sa.Column("available_cash", sa.Numeric(precision=18, scale=2), server_default="1000000.00", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_paper_accounts_user_id", "paper_trading_accounts", ["user_id"])

    # 2. paper_orders
    op.create_table(
        "paper_orders",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Uuid(as_uuid=True), sa.ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("order_type", sa.String(length=20), server_default="MARKET", nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("requested_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("executed_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="PENDING", nullable=False),
        sa.Column("rejection_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_paper_orders_account_id", "paper_orders", ["account_id"])
    op.create_index("ix_paper_orders_instrument_id", "paper_orders", ["instrument_id"])
    op.create_index("ix_paper_orders_status", "paper_orders", ["status"])

    # 3. paper_positions
    op.create_table(
        "paper_positions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Uuid(as_uuid=True), sa.ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), server_default="0", nullable=False),
        sa.Column("average_entry_price", sa.Numeric(precision=18, scale=4), server_default="0", nullable=False),
        sa.Column("realized_pnl", sa.Numeric(precision=18, scale=2), server_default="0.00", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("account_id", "instrument_id", name="uq_account_instrument_position"),
    )
    op.create_index("ix_paper_positions_account_id", "paper_positions", ["account_id"])
    op.create_index("ix_paper_positions_instrument_id", "paper_positions", ["instrument_id"])

    # 4. paper_trades
    op.create_table(
        "paper_trades",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Uuid(as_uuid=True), sa.ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("execution_price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fees", sa.Numeric(precision=18, scale=2), server_default="0.00", nullable=False),
        sa.Column("slippage", sa.Numeric(precision=18, scale=4), server_default="0.00", nullable=False),
        sa.Column("realized_pnl", sa.Numeric(precision=18, scale=2), server_default="0.00", nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_paper_trades_account_id", "paper_trades", ["account_id"])
    op.create_index("ix_paper_trades_order_id", "paper_trades", ["order_id"])
    op.create_index("ix_paper_trades_instrument_id", "paper_trades", ["instrument_id"])

    # 5. paper_portfolio_snapshots
    op.create_table(
        "paper_portfolio_snapshots",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("cash", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("positions_value", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_equity", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("realized_pnl", sa.Numeric(precision=18, scale=2), nullable=False),
    )
    op.create_index("ix_paper_snapshots_account_id", "paper_portfolio_snapshots", ["account_id"])

    # 6. backtest_jobs
    op.create_table(
        "backtest_jobs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("strategy_name", sa.String(length=50), nullable=False),
        sa.Column("symbol", sa.String(length=30), nullable=False),
        sa.Column("initial_capital", sa.Numeric(precision=18, scale=2), server_default="1000000.00", nullable=False),
        sa.Column("parameters_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="QUEUED", nullable=False),
        sa.Column("error_message", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_backtest_jobs_user_id", "backtest_jobs", ["user_id"])
    op.create_index("ix_backtest_jobs_status", "backtest_jobs", ["status"])

    # 7. backtest_results
    op.create_table(
        "backtest_results",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_id", sa.Uuid(as_uuid=True), sa.ForeignKey("backtest_jobs.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("initial_capital", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("final_equity", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_pnl", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_return_pct", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("max_drawdown_pct", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("trade_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("win_rate_pct", sa.Numeric(precision=18, scale=2), server_default="0.00", nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("equity_curve_json", sa.JSON(), nullable=False),
        sa.Column("trades_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_backtest_results_job_id", "backtest_results", ["job_id"])


def downgrade() -> None:
    op.drop_table("backtest_results")
    op.drop_table("backtest_jobs")
    op.drop_table("paper_portfolio_snapshots")
    op.drop_table("paper_trades")
    op.drop_table("paper_positions")
    op.drop_table("paper_orders")
    op.drop_table("paper_trading_accounts")
