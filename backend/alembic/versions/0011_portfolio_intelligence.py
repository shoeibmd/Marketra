"""portfolio intelligence snapshots

Revision ID: 0011_portfolio_intelligence
Revises: 0010_controlled_live_trading
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0011_portfolio_intelligence"
down_revision: Union[str, None] = "0010_controlled_live_trading"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "portfolio_analytics_snapshots",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("total_equity", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("cash_balance", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("positions_value", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("realized_pnl", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("drawdown_pct", sa.Numeric(precision=18, scale=2), server_default="0.00", nullable=False),
        sa.Column("exposure_json", sa.JSON(), nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_portfolio_analytics_user_id", "portfolio_analytics_snapshots", ["user_id"])
    op.create_index("ix_portfolio_analytics_account_id", "portfolio_analytics_snapshots", ["account_id"])
    op.create_index("ix_portfolio_analytics_timestamp", "portfolio_analytics_snapshots", ["timestamp"])


def downgrade() -> None:
    op.drop_table("portfolio_analytics_snapshots")
